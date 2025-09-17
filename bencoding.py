from typing import Any
from string import digits

TOKEN_INT: int = ord("i")
TOKEN_LIST: int = ord("l")
TOKEN_DICT: int = ord("d")
TOKEN_STR_SPLIT: int = ord(":")
TOKEN_END: int = ord("e")

def decode(encoded: bytes) -> int | bytes | list[Any] | dict[bytes, Any]:
    """Decode bencoded data"""

    def decodeNext(index: int) -> tuple[int | bytes | list[Any] | dict[bytes, Any], int]:
        if encoded[index] == TOKEN_INT:
            return decodeInt(index)
        elif encoded[index] == TOKEN_LIST:
            return decodeList(index)
        elif encoded[index] == TOKEN_DICT:
            return decodeDict(index)
        else:
            return decodeStr(index)

    def decodeInt(index: int) -> tuple[int, int]:
        if encoded[index] != TOKEN_INT:
            raise Exception(f"Wrong token at {index}, expected {TOKEN_INT}, found {encoded[index]}")
        end: int = 0

        for i in range(index, len(encoded)):
            if encoded[i] == TOKEN_END:
                end = i
                break

        if end == 0:
            raise ValueError(f"No end token ({TOKEN_END}) found")

        number = encoded[index + 1:end]

        if number.startswith(b"0") and len(number) > 1:
            raise ValueError(f"Leading zero in number {number.decode()}")

        if number == b"-0":
            raise ValueError("Negative zero not valid bencode")

        out = int(number)

        return out, end + 1
    
    def decodeStr(index: int) -> tuple[bytes, int]:
        if chr(encoded[index]) not in digits:
            raise ValueError(f"Attempting to parse as a string but no digits at index {index}")

        end = 0

        for i in range(index, len(encoded)):
            if encoded[i] == TOKEN_STR_SPLIT:
                end = i
                break

        if end == 0:
            raise ValueError(f"No end token ({TOKEN_STR_SPLIT}) found")  

        length = int(encoded[index:end].decode())

        string = encoded[end + 1:end + length + 1]

        return string, end + length + 1

    def decodeList(index: int) -> tuple[list[Any], int]:
        if encoded[index] != TOKEN_LIST:
            raise ValueError(f"Wrong token at {index}, expected {TOKEN_LIST}, found {encoded[index]}")

        output: list[Any] = []
        current_index = index + 1

        while encoded[current_index] != TOKEN_END:
            to_add, current_index = decodeNext(current_index)
            output.append(to_add)

            if current_index >= len(encoded):
                raise ValueError(f"Missing end token {TOKEN_END}")

        return output, current_index + 1

    def decodeDict(index: int) -> tuple[dict[bytes, Any], int]:
        output: dict[bytes, Any] = {}
        current_index = index + 1

        while encoded[current_index] != TOKEN_END:
            key, current_index = decodeStr(current_index)
            value, current_index = decodeNext(current_index)

            if current_index >= len(encoded):
                raise ValueError(f"Missing end token {TOKEN_END}")

            output[key] = value

        return output, current_index + 1

    result, final = decodeNext(0)

    if final != len(encoded):
        raise ValueError("Trailing data after valid bencode")

    return result

def encode(original: int | bytes | list[Any] | dict[bytes, Any]) -> bytes:
    """Encode data into bencode"""

    if isinstance(original, bytes):
        return str(len(original)).encode() + bytes([TOKEN_STR_SPLIT]) + original
    elif isinstance(original, int):
        return bytes([TOKEN_INT]) + str(original).encode() + bytes([TOKEN_END])
    elif isinstance(original, list):
        return bytes([TOKEN_LIST]) + b''.join(encode(obj) for obj in original) + bytes([TOKEN_END])
    elif isinstance(original, dict):
        return \
            bytes([TOKEN_DICT]) + \
            b''.join(encode(key) + encode(value) for key, value in sorted(original.items(), key=lambda x: x[0])) + \
            bytes([TOKEN_END])
    else:
        raise TypeError("Wrong input type")

# Example usage
if __name__ == "__main__":
    bencode: bytes = b'd3:bar4:spam3:fooi42e4:listl3:one3:two5:threeee'
    print(decode(bencode)) # -> {b'bar': b'spam', b'foo': 42, b'list': [b'one', b'two', b'three']}

    to_encode: dict[bytes, Any] = {b"spam": b"eggs", b"names": [b"Alan", b"Bob", b"Joe"], b"magic number": 42}
    print(encode(to_encode)) # -> b'd12:magic numberi42e5:namesl4:Alan3:Bob3:Joee4:spam4:eggse'