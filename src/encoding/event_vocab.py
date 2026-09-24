class EventVocab:
    def __init__(self):
        self.token2id = {
            "<PAD>": 0,
            "<UNK>": 1,
            "PROCESS:CREATE": 2,
            "API:READ_FILE": 3,
            "API:WRITE_FILE": 4,
            "API:RENAME_FILE": 5,
            "API:CRYPT_ENCRYPT": 6,
            "API:OPEN_FILE": 7,
            "API:CLOSE_FILE": 8,
            "REGISTRY:READ_KEY": 9,
            "REGISTRY:SET_KEY": 10,
            "RESOURCE:CPU_MEM": 11,
            "NETWORK:CONNECT": 12,
            "NETWORK:DNS_QUERY": 13
        }

    def encode(self, seq):
        return [self.token2id.get(t, 1) for t in seq]
