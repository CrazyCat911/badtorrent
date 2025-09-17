from typing import Optional, Any
import bencoding
import hashlib

class TorrentFile:
    path: str
    data: Optional[dict[bytes, Any]]  # Full decoded torrent dictionary
    info: Optional[dict[bytes, Any]]  # 'info' section of torrent
    info_hash: Optional[bytes]        # SHA1 hash of bencoded 'info'

    def __init__(self, path: str) -> None:
        self.path = path
        self.data = None
        self.info = None
        self.info_hash = None

    def load(self) -> None:
        """Load and decode the .torrent file."""
        with open(self.path, "rb") as f:
            data = bencoding.decode(f.read())

        if not isinstance(data, dict):
            raise TypeError(".torrent file is not a dictionary")

        self.data = data

        if b"info" not in self.data:
            raise ValueError(".torrent file does not have an info dictionary")
        if not isinstance(self.data[b"info"], dict):
            raise TypeError("info not a dictionary")

        self.info = self.data[b"info"]
        self.compute_info_hash()


    def compute_info_hash(self) -> None:
        """Compute SHA1 hash of bencoded 'info' dictionary."""

        if not isinstance(self.info, dict):
            raise TypeError("info not a dictionary")

        encoded = bencoding.encode(self.info)

        self.info_hash = hashlib.sha1(encoded).digest()

    def get_announce_url(self) -> Optional[bytes]:
        """Return the tracker URL from the torrent."""
        if not isinstance(self.data, dict):
            raise TypeError("info not a dictionary")

        if b"announce" in self.data:
            return self.data[b"announce"]
        
        raise ValueError("No announce URL in self.data")

    def get_file_info(self) -> dict[str, Any]:
        """Return basic file info."""
        if not isinstance(self.info, dict):
            raise TypeError("self.info not a dictionary")

        if not all(key in self.info for key in [b"name", b"length", b"piece length", b"pieces"]):
            raise ValueError("Not all required keys in info dictionary")

        return {
            "name": self.info[b"name"],
            "length": self.info[b"length"],
            "piece length": self.info[b"piece length"],
            "pieces": self.info[b"pieces"]
        }

# Example usage
if __name__ == "__main__":
    torrentfile = TorrentFile("my_cool_torrent.torrent")
    torrentfile.load()

    print(f"""
Announce URL: {torrentfile.get_announce_url()}
Info hash: {torrentfile.info_hash}
File info: {torrentfile.get_file_info()}
""")
