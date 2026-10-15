import os
import pandas as pd

from feature_extractor import Signature


class DatasetLoader:

    def __init__(self):

        self.rows = []

    # ---------------------------------------------------------

    def process_folder(self, folder):

        print(f"\nScanning : {folder}")

        total = 0

        success = 0

        for root, _, files in os.walk(folder):

            for file in files:

                if not file.lower().endswith(".txt"):

                    continue

                total += 1

                path = os.path.join(root, file)

                try:

                    sig = Signature(path)

                    features = sig.extract_features()

                    label = self.get_label(file)

                    features["label"] = label

                    self.rows.append(features)

                    success += 1

                except Exception as e:

                    print(f"Skipped {file} : {e}")

        print(f"Processed {success}/{total}")

    # ---------------------------------------------------------

    def get_label(self, filename):

        try:

            number = int(

                "".join(

                    filter(

                        str.isdigit,

                        filename.split("S")[-1]

                    )

                )

            )

            return 1 if number <= 20 else 0

        except:

            return 0

    # ---------------------------------------------------------

    def build(self, folders):

        self.rows = []

        for folder in folders:

            self.process_folder(folder)

        df = pd.DataFrame(self.rows)

        return df

    # ---------------------------------------------------------

    def save(

        self,

        folders,

        output="training_dataset.csv"

    ):

        df = self.build(folders)

        df.to_csv(

            output,

            index=False

        )

        print("\nDataset Created")

        print(df.shape)

        print(df.head())

        print(f"\nSaved -> {output}")


if __name__ == "__main__":

    DATASETS = [

        r"D:\Downloads\Task1\Task1",

        r"D:\Downloads\Task2\Task2"

    ]

    loader = DatasetLoader()

    loader.save(DATASETS)