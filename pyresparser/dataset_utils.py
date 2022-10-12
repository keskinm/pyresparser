from __future__ import print_function, unicode_literals
import itertools
import json
import copy
from googletrans import Translator


def determine(ls):
    """Excludes overlapping entities."""
    exclude = []
    combs = itertools.combinations(ls, 2)
    for a, b in combs:
        x = range(a['points'][0]['start'], a['points'][0]['end'])
        y = range(b['points'][0]['start'], b['points'][0]['end'])
        xs = set(x)
        res = xs.intersection(y)
        if res != set():
            exclude.append(a)
            exclude.append(b)

        if a['points'][0]['start'] == b['points'][0]['start']:
            exclude.append(a)
            exclude.append(b)

        if a['points'][0]['end'] == b['points'][0]['end']:
            exclude.append(a)
            exclude.append(b)

    for item in ls:
        if item['points'][0]['end'] - item['points'][0]['start'] < 3:
            exclude.append(item)

    fin = []

    for item in ls:
        if item not in exclude:
            fin.append(item)

    return fin


class ProtoEnFrTranslator:
    @staticmethod
    def translate(string, *_, **__):
        return string


translator = Translator()


def append_to_json(_dict, path):
    """Append dict to json file."""
    with open(path, 'ab+') as f:
        f.seek(0, 2)  # Go to the end of file
        if f.tell() == 0:  # Check if file is empty
            f.write(json.dumps([_dict]).encode())  # If empty, write an array
        else:
            f.seek(-1, 2)
            f.truncate()  # Remove the last character, open the array
            f.write(' , '.encode())  # Write the separator
            f.write(json.dumps(_dict).encode())  # Dump the dictionary
            f.write(']'.encode())


with open("pyresparser/traindata_fr.json", "r", encoding="utf-8") as fopen:
    done = fopen.readlines()[0]
    done = json.loads(done)
    done = len(done)


with open("pyresparser/traindata.json", "r", encoding="utf-8") as fopen:
    data = fopen.readlines()

line_idx = 0

for line in data[done:]:
    line_idx+=1
    print(700-done-line_idx)
    line = json.loads(line)

    translated_annotations = []

    if not line["annotation"]:
        continue

    clean_annotations = determine(line['annotation'])
    clean_annotations = sorted(clean_annotations, key=lambda a: a["points"][0]["start"])

    _clean_annotations = []
    for annotation in clean_annotations:
        point = annotation["points"][0]
        if line["content"][point["start"]:point["end"]+1] == point["text"]:
            _clean_annotations.append(annotation)
    clean_annotations = _clean_annotations

    indices = []
    for annotation in clean_annotations:
        indices.append((annotation["points"][0]["start"]))
        indices.append((annotation["points"][0]["end"]+1))

    if len(set(indices)) != len(indices):
        continue

    if indices[0] != 0:
        indices.insert(0, 0)
        inserted = True
    else:
        inserted = False

    content_chunks = [line["content"][indices[0]:indices[1]]]
    content_chunks += [line["content"][i:j] for i, j in zip(indices[1:], indices[2:])]
    content_chunks.append(line["content"][indices[-1]:])

    translated_content_chunks = []
    for chunk in content_chunks:
        try:
            s = translator.translate(chunk, dest='fr', src='en').text
        except (IndexError, TypeError, AttributeError):
            s = chunk
        translated_content_chunks.append(s)

    translated_content = "".join(translated_content_chunks)

    for annotation_idx, annotation in enumerate(clean_annotations):
        point = annotation["points"][0]
        translated_annotation = copy.deepcopy(annotation)
        translated_point = copy.deepcopy(point)

        try:
            translated_annotation["label"] = [translator.translate(ll, dest='fr', src='en').text for ll in translated_annotation["label"]]
        except AttributeError:
            break

        translated_point["text"] = translated_content_chunks[annotation_idx*2+int(inserted)]
        translated_point["start"] = translated_content.index(translated_point["text"])
        translated_point["end"] = translated_point["start"]+len(translated_point["text"])-1

        translated_annotation["points"] = [translated_point]
        translated_annotations.append(translated_annotation)

    for translated_annotation in translated_annotations:
        translated_point = translated_annotation["points"][0]
        if translated_content[translated_point["start"]:translated_point["end"]+1] != translated_point["text"]:
            print(translated_content[translated_point["start"]:translated_point["end"]+1])
            print(translated_point["text"])
            raise ValueError("Mis alignments should be excluded before translation.")

    translated_line = {"content": translated_content,
                       "annotation": translated_annotations,
                       "extras": line["extras"],
                       "metadata": line["metadata"]}

    append_to_json(translated_line, "pyresparser/traindata_fr.json")
