from training.feature_extractor import Signature


class FeatureExtractor:

    @staticmethod
    def extract(signature):

        sig = Signature(signature)

        return sig.extract_features()