from __future__ import print_function, unicode_literals
import itertools
import json
import copy


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
    def translate(string):
        return string


translator = ProtoEnFrTranslator()

translated_lines = []

with open("pyresparser/traindata.json", "r", encoding="utf-8") as fopen:
    data = fopen.readlines()


for line in data:
    line = json.loads(line)

    translated_annotations = []

    if line["annotation"] is None:
        continue

    clean = determine(line['annotation'])
    clean = sorted(clean, key=lambda a: a["points"][0]["start"])

    for annotation in clean:
        point = annotation["points"][0]
        if line["content"][point["start"]:point["end"]+1] != point["text"]:
            continue

        translated_annotation = copy.deepcopy(annotation)
        translated_point = copy.deepcopy(point)

        translated_annotation["label"] = [translator.translate(ll) for ll in translated_annotation["label"]]
        translated_point["text"] = translator.translate(translated_point["text"])
        translated_annotation["points"] = [translated_point]
        translated_annotations.append(translated_annotation)

    translated_content = translator.translate(line["content"])
    for translated_annotation in translated_annotations:
        translated_point = translated_annotation["points"][0]
        if translated_content[translated_point["start"]:translated_point["end"] + 1] != translated_point["text"]:
            print(translated_content[translated_point["start"]:translated_point["end"] + 1])
            print(translated_point["text"])
            raise ValueError("Mis alignments should be excluded before translation.")

    translated_line = {"content": translated_content,
                       "annotation": translated_annotations,
                       "extras": line["extras"],
                       "metadata": line["metadata"]}
