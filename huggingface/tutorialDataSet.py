# load a dataset builder and inspect a dataset’s attributes without committing to downloading it:

from datasets import load_dataset_builder, load_dataset
ds_builder = load_dataset_builder("rotten_tomatoes")

print(ds_builder.info.description)

print(ds_builder.info.features)

# load dataset
dataset = load_dataset('rotten_tomatoes', split='train')[0]
print(dataset)

# les Splits du dataset (ici ...  train validation et test)
from datasets import get_dataset_split_names
print( get_dataset_split_names("rotten_tomatoes") )


# Some datasets contain several sub-datasets.  par exemple minds14 avec des versions par langues
from datasets import get_dataset_config_names

configs = get_dataset_config_names("PolyAI/minds14")
print(configs)

#le dernier element du dataset est donné par -1
print(dataset[-1])

# l ensemble des valeurs de la colonne ici : 'text' ou label
print(dataset["label"])
# Get the first three rows
dataset[:3]
# Get rows between three and six
dataset[3:6]
