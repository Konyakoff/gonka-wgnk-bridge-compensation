"""Мост WGNK: декодеры событий и вывод адресов из публичного ключа.

Как связаны кошельки двух сетей (проверено 30.09.2026 на пяти реальных
транзакциях `MsgRequestBridgeMint`, где публичный ключ подписанта виден прямо
в ответе узла):

- `gonka1...` = bech32("gonka", ripemd160(sha256(сжатый pubkey))) — совпало
  5 из 5, это стандартный адрес Cosmos;
- `0x...`     = keccak256(несжатый pubkey)[12:] — у 2 из 5 совпал с адресом
  назначения в той же транзакции, то есть часть людей действительно держит
  один ключ в обеих сетях.

Отсюда три источника связи адресов (`gonka.address_links.source`):
`bridge_mint` — прямая пара из сообщения Gonka; `burn` — адрес выведен из
подписи burn-транзакции Ethereum; `same_key` — оба адреса выведены из одного
ключа, что само по себе прохода через мост не доказывает.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from decimal import Decimal

from app.services.gonka.constants import (
    GONKA_BECH32_PREFIX,
    TOPIC_WGNK_BURNED,
    TOPIC_WGNK_MINTED,
    WGNK_DECIMALS,
)
from app.services.gonka.uniswap import _words, hex_int, log_meta, topic_address

# ── bech32 (BIP-173) ─────────────────────────────────────────────────────────
# Свои 20 строк вместо зависимости: формат стабилен, а лишний пакет в образе
# ради кодирования адреса не нужен.
_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _bech32_polymod(values: list[int]) -> int:
    gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for v in values:
        top = chk >> 25
        chk = ((chk & 0x1FFFFFF) << 5) ^ v
        for i in range(5):
            chk ^= gen[i] if (top >> i) & 1 else 0
    return chk


def _hrp_expand(hrp: str) -> list[int]:
    return [ord(c) >> 5 for c in hrp] + [0] + [ord(c) & 31 for c in hrp]


def _convertbits(data: bytes, frm: int, to: int) -> list[int]:
    acc = bits = 0
    out: list[int] = []
    maxv = (1 << to) - 1
    for value in data:
        acc = (acc << frm) | value
        bits += frm
        while bits >= to:
            bits -= to
            out.append((acc >> bits) & maxv)
    if bits:
        out.append((acc << (to - bits)) & maxv)
    return out


def bech32_encode(hrp: str, payload: bytes) -> str:
    data = _convertbits(payload, 8, 5)
    checksum_input = _hrp_expand(hrp) + data + [0] * 6
    polymod = _bech32_polymod(checksum_input) ^ 1
    checksum = [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(_CHARSET[d] for d in data + checksum)


# ── Хеши ─────────────────────────────────────────────────────────────────────
def _ripemd160(data: bytes) -> bytes:
    """RIPEMD-160: сперва hashlib, иначе pycryptodome.

    В сборках с OpenSSL 3 ripemd160 бывает отключён в hashlib, поэтому нужен
    запасной путь (pycryptodome всё равно стоит в зависимостях ради keccak).
    """
    try:
        return hashlib.new("ripemd160", data).digest()
    except ValueError:  # pragma: no cover — зависит от сборки OpenSSL
        from Crypto.Hash import RIPEMD160

        return RIPEMD160.new(data).digest()


def keccak256(data: bytes) -> bytes:
    """keccak-256 (не SHA3!) — тот, которым Ethereum считает адреса и топики."""
    from Crypto.Hash import keccak as _keccak

    return _keccak.new(digest_bits=256, data=data).digest()


# ── Адреса из публичного ключа ───────────────────────────────────────────────
_SECP256K1_P = 2**256 - 2**32 - 977


def decompress_pubkey(pubkey: bytes) -> bytes:
    """Сжатый ключ (33 байта) → несжатый без префикса 0x04 (64 байта).

    Если ключ уже несжатый — возвращаем его 64-байтовую часть.
    """
    if len(pubkey) == 64:
        return pubkey
    if len(pubkey) == 65 and pubkey[0] == 0x04:
        return pubkey[1:]
    if len(pubkey) != 33 or pubkey[0] not in (0x02, 0x03):
        raise ValueError(f"неожиданный формат публичного ключа: {len(pubkey)} байт")
    x = int.from_bytes(pubkey[1:], "big")
    y = pow((x**3 + 7) % _SECP256K1_P, (_SECP256K1_P + 1) // 4, _SECP256K1_P)
    if (y & 1) != (pubkey[0] & 1):
        y = _SECP256K1_P - y
    return x.to_bytes(32, "big") + y.to_bytes(32, "big")


def compress_pubkey(pubkey: bytes) -> bytes:
    """Несжатый ключ (64 или 65 байт) → сжатый (33 байта)."""
    if len(pubkey) == 33:
        return pubkey
    body = pubkey[1:] if len(pubkey) == 65 else pubkey
    x, y = body[:32], body[32:]
    return bytes([0x02 + (y[-1] & 1)]) + x


def gonka_address_from_pubkey(pubkey: bytes) -> str:
    """Публичный ключ → адрес Gonka (стандартная схема Cosmos)."""
    compressed = compress_pubkey(pubkey)
    return bech32_encode(GONKA_BECH32_PREFIX, _ripemd160(hashlib.sha256(compressed).digest()))


def eth_address_from_pubkey(pubkey: bytes) -> str:
    """Публичный ключ → адрес Ethereum в нижнем регистре."""
    return "0x" + keccak256(decompress_pubkey(pubkey))[12:].hex()


def recover_pubkey_from_tx(tx: dict) -> bytes | None:
    """Публичный ключ отправителя из подписи транзакции Ethereum.

    Работает для legacy, EIP-2930 и EIP-1559 (`type` 0/1/2). Возвращает None,
    если подписи нет или тип транзакции нам незнаком: тогда связь по ключу
    просто не выводится, а сама запись о burn всё равно сохраняется.
    """
    try:
        from eth_account._utils.legacy_transactions import (
            serializable_unsigned_transaction_from_dict,
        )
        from eth_account._utils.signing import extract_chain_id, to_standard_v
        try:  # eth-account ≥ 0.10 перенёс модуль; со старым путём функция молча возвращала None
            from eth_account.typed_transactions import TypedTransaction
        except ImportError:
            from eth_account._utils.typed_transactions import TypedTransaction
        from eth_keys.datatypes import Signature
        from eth_utils import to_checksum_address
    except ImportError:  # pragma: no cover — пакет ставится вместе с образом
        return None

    def _i(key: str) -> int | None:
        return hex_int(tx.get(key))

    r, s = _i("r"), _i("s")
    v = _i("v") if tx.get("v") is not None else _i("yParity")
    if r is None or s is None or v is None:
        return None
    tx_type = _i("type") or 0
    try:
        if tx_type == 0:
            chain_id, standard_v = extract_chain_id(v)
            unsigned = serializable_unsigned_transaction_from_dict({
                "nonce": _i("nonce"),
                "gasPrice": _i("gasPrice"),
                "gas": _i("gas"),
                "to": bytes.fromhex((tx.get("to") or "").removeprefix("0x")) if tx.get("to") else b"",
                "value": _i("value") or 0,
                "data": bytes.fromhex((tx.get("input") or "0x").removeprefix("0x")),
                **({"chainId": chain_id} if chain_id is not None else {}),
            })
            msg_hash = unsigned.hash()
            standard_v = to_standard_v(standard_v)   # extract_chain_id отдаёт 27/28, Signature ждёт 0/1
        else:
            payload = {
                "type": tx_type,
                "chainId": _i("chainId") or 1,
                "nonce": _i("nonce"),
                "gas": _i("gas"),
                # eth-account 0.14 принимает адреса только в checksum-виде (EIP-55).
                "to": to_checksum_address(tx["to"]) if tx.get("to") else "",
                "value": _i("value") or 0,
                "data": tx.get("input") or "0x",
                "accessList": [{"address": to_checksum_address(a["address"]), "storageKeys": a.get("storageKeys") or []}
                               for a in tx.get("accessList") or []],
            }
            if tx_type == 1:
                payload["gasPrice"] = _i("gasPrice")
            else:
                payload["maxFeePerGas"] = _i("maxFeePerGas")
                payload["maxPriorityFeePerGas"] = _i("maxPriorityFeePerGas")
            if tx_type == 4:   # EIP-7702: список авторизаций входит в подписываемые данные
                payload["authorizationList"] = [
                    {"chainId": hex_int(a.get("chainId")) or 0, "address": to_checksum_address(a["address"]), "nonce": hex_int(a.get("nonce")) or 0,
                     "yParity": hex_int(a.get("yParity")) or 0, "r": hex_int(a.get("r")), "s": hex_int(a.get("s"))}
                    for a in tx.get("authorizationList") or []]
            msg_hash = TypedTransaction.from_dict(payload).hash()
            standard_v = to_standard_v(v)
        pub = Signature(vrs=(standard_v, r, s)).recover_public_key_from_msg_hash(msg_hash)
    except Exception:  # noqa: BLE001 — незнакомый формат подписи не должен ронять шаг
        return None
    recovered = pub.to_bytes()
    expected = (tx.get("from") or "").lower()
    if expected and eth_address_from_pubkey(recovered) != expected:
        return None
    return recovered


# ── События моста ────────────────────────────────────────────────────────────
def bridge_event_values(log: dict) -> dict | None:
    """Лог контракта WGNK → строка `gonka.bridge_events` (или None, если не наше).

    Сигнатуры взяты из верифицированного ABI:
    `WGNKMinted(uint64 indexed epochId, bytes32 indexed requestId,
                address indexed recipient, uint256 amount)`
    `WGNKBurned(address indexed from, uint256 amount, uint256 timestamp)`
    """
    topics = log.get("topics") or []
    if not topics:
        return None
    topic0 = (topics[0] or "").lower()
    # У таблицы моста нет колонок газа и позиции в блоке — берём из метаданных
    # только то, что в неё складывается, иначе вставка упадёт на лишних полях.
    meta = {k: v for k, v in log_meta(log).items()
            if k in ("block_number", "block_time", "tx_hash", "log_index")}
    words = _words(log.get("data"))
    if topic0 == TOPIC_WGNK_MINTED:
        amount = words[0] if words else None
        return {
            "kind": "mint",
            "epoch_id": hex_int(topics[1]) if len(topics) > 1 else None,
            "request_id": (topics[2] or "").lower() if len(topics) > 2 else None,
            "recipient": topic_address(topics[3] if len(topics) > 3 else None),
            "from_addr": None,
            "amount_raw": amount,
            "amount_wgnk": (Decimal(amount).scaleb(-WGNK_DECIMALS)
                            if amount is not None else None),
            "burn_timestamp": None,
            "link_status": "pending",
            "raw_json": {"log": log},
            **meta,
        }
    if topic0 == TOPIC_WGNK_BURNED:
        amount = words[0] if words else None
        burn_ts = words[1] if len(words) > 1 else None
        return {
            "kind": "burn",
            "epoch_id": None,
            "request_id": None,
            "recipient": None,
            "from_addr": topic_address(topics[1] if len(topics) > 1 else None),
            "amount_raw": amount,
            "amount_wgnk": (Decimal(amount).scaleb(-WGNK_DECIMALS)
                            if amount is not None else None),
            "burn_timestamp": burn_ts,
            "link_status": "pending",
            "raw_json": {"log": log},
            **meta,
        }
    return None


def utc(ts: int | None) -> datetime | None:
    return datetime.fromtimestamp(ts, tz=timezone.utc) if ts else None
