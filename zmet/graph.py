from flask import Blueprint, redirect, render_template, request, current_app, url_for
import json
from . import config
from flask_wtf.csrf import generate_csrf

OBJECTS = []
NAME_TO_OBJECT = {}

graph_bp = Blueprint("graph", __name__, url_prefix="/graph", template_folder="templates")

def add_node(name=None, data=None):
    index = len(OBJECTS)
    if name is None:
        name = "node_{uid}"
    if "{uid}" in name:
        name = name.format(uid=index)
    assert name.isidentifier()
    node = Node(name, index, data)
    current_app.logger.info(f"adding node { name }")
    OBJECTS.append(node)
    NAME_TO_OBJECT[name] = node
    return node


def add_edge(o, p, s, name=None):
    index = len(OBJECTS)
    if name is None:
        name = "edge_" + str(index)
    edge = Edge(o, p, s, name, index)
    current_app.logger.info(f"adding edge { name } ({o} {p} {s})")
    OBJECTS.append(edge)
    NAME_TO_OBJECT[name] = edge
    if type(o) in (Node, Edge): # to enable pseudo nodes on load
        print("wireing graph")
        o.oof.add(edge)
        p.pof.add(edge)
        s.sof.add(edge)
    return edge


def add_str(data):
    obj = add_node("str_{uid}", data)
    add_edge(obj, get_or_create("class"), get_or_create("str"))
    return obj


def get_or_create(name):
    obj = NAME_TO_OBJECT.get(name)
    if obj is None:
        obj = add_node(name)
    return obj


class Node:
    def __init__(self, name, index, data):
        self.name = name
        self.index = index
        self.data = data
        self.oof = set()
        self.pof = set()
        self.sof = set()

    def __repr__(self) -> str:
        return f"{self.name}"

    def a(self):
        return f"<a href=/graph/obj/{ self.name }>{ self.name }</a>"

    def __getattr__(self, name: str):
        if name[-1] == "s":
            return [x.s for x in self.oof if x.p.name == name[:-1]]
        else:
            items = [x.s for x in self.oof if x.p.name == name]
            if not items:
                raise AttributeError("attribute not defined")
            if len(items) > 1:
                raise AttributeError("duplicate definitions")
            return items[0]


class Edge:
    def __init__(self, o, p, s, name, index):
        self.o = o
        self.p = p
        self.s = s
        self.name = name
        self.index = index

    def __repr__(self) -> str:
        return f"({self.o.name} {self.p.name} {self.s.name})"

    def a(self):
        return f"<a href=/graph/obj/{ self.name }>{ self.name }</a>"

    def aa(self):
        return f"{ self.o.a() } { self.p.a() } { self.s.a() } ({ self.a() })"


def serialize():
    to_serialize = []
    for obj in OBJECTS:
        if isinstance(obj, Node):
            to_serialize.append({
                "type": "Node",
                "name": obj.name,
                "data": obj.data,
            })
        if isinstance(obj, Edge):
            to_serialize.append({
                "type": "Edge",
                "name": obj.name,
                "object_index": obj.o.index,
                "predicate_index": obj.p.index,
                "subject_index": obj.s.index,
            })
    return to_serialize

@graph_bp.route("/")
def index():
    return redirect(url_for("graph.explore"))

@graph_bp.route("/save")
def save():
    return save_inner()

def save_inner():
    current_app.logger.info("saving graph")
    with open(config.cache_path + "/graph.json", "w") as f:
        json.dump(serialize(), f, indent=4)
    message = f"sucess: { len(OBJECTS) } objects saved"
    current_app.logger.info(message)
    return message

@graph_bp.route("/clear")
def clear():
    current_app.logger.info("clearing graph")
    global OBJECTS
    global NAME_TO_OBJECT
    OBJECTS = []
    NAME_TO_OBJECT = {}
    save_inner()
    message = f"sucess: cleared"
    current_app.logger.info(message)
    return message


@graph_bp.route("/load")
def load():
    current_app.logger.info("loading graph")
    global OBJECTS
    OBJECTS = []
    try:
        with open(config.cache_path + "/graph.json", "r") as f:
            obj_list = json.load(f)

        for obj in obj_list:
            if obj["type"] == "Node":
                add_node(obj["name"], obj["data"])
            if obj["type"] == "Edge":
                add_edge(
                    obj["object_index"],
                    obj["predicate_index"],
                    obj["subject_index"],
                    obj["name"],
                )

        for obj in OBJECTS:
            if isinstance(obj, Edge):
                obj.o = OBJECTS[obj.o]
                obj.p = OBJECTS[obj.p]
                obj.s = OBJECTS[obj.s]
                obj.o.oof.add(obj)
                obj.p.pof.add(obj)
                obj.s.sof.add(obj)
    except FileNotFoundError:
        pass

    message = f"sucess: { len(OBJECTS) } objects loaded"
    current_app.logger.info(message)
    return message


@graph_bp.route("/add", methods=["GET"])
def add_get():
    return f"""
        <form method="post">
          <textarea rows="10" cols="50" name="text"></textarea>
          <input type="submit">
          <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
    """

TRANSACTION = []

@graph_bp.route("/add", methods=["POST"])
def add_post():
    text = request.form.get("text")
    if text is None: return "no text found"
    # parse(text)
    actions = parse_addition_block(text)
    current_app.logger.info("== add ==")
    for action in actions:
        current_app.logger.info(str(action))
    current_app.logger.info("==  .  ==")
    global TRANSACTION
    TRANSACTION = actions
    return redirect(url_for("graph.transaction_get"))


@graph_bp.route("/transaction", methods=["GET"])
def transaction_get():
    button = f"""
        <form method="post">
          <input type="submit">
          <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
    """
    return "<br />".join(map(str, TRANSACTION)) + "<br />" + button


@graph_bp.route("/transaction", methods=["POST"])
def transaction_post():
    try:
        # TODO: atomic transactions
        for action in TRANSACTION:
            action.eval()
    except Exception as e:
        return str(e)
    return "success"


@graph_bp.route("/all")
def list_all():
    return redirect(url_for("graph.search", q="? ? ?"))


def query(o='?', p='?', s='?'):
    res = []
    for obj in OBJECTS:
        if not isinstance(obj, Edge):
            continue
        if o != '?' and obj.o.name != o:
            continue
        if p != '?' and obj.p.name != p:
            continue
        if s != '?' and obj.s.name != s:
            continue
        res.append(obj)
    return res


@graph_bp.route("/search", methods=["GET"])
def search():
    q = request.args.get("q")
    if q is not None:
        items = query(*q.split(" "))
        items = [f"<li>{ x.aa() }</li>" for x in items]
        return f"""
        <a href="/graph/add">add</a><br />
        <h3>There is { len(items) } search results:</h3><br />
        <ol>{ "".join(items) }</ol>
        """
    return f"""
        <form method="get">
          <input type="text" name="q">
          <input type="submit">
          <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
    """

@graph_bp.route("/obj/<name>")
def get_obj(name):
    obj = NAME_TO_OBJECT.get(name)
    if obj is None:
        return "not found"
    
    return f"""
        <h1>{ name }</h1><br />
        <ul>
        { "".join(
            f"<li><b>{ x.o.a() }</b> { x.p.a() } { x.s.a() }</li>"
            for x in query(o=obj.name)
        ) }
        </ul>
        <ul>
        { "".join(
            f"<li>{ x.o.a() } <b>{ x.p.a() }</b> { x.s.a() }</li>"
            for x in query(p=obj.name)
        ) }
        </ul>
        <ul>
        { "".join(
            f"<li>{ x.o.a() } { x.p.a() } <b>{ x.s.a() }</b></li>"
            for x in query(s=obj.name)
        ) }
        </ul>
    """

@graph_bp.route("/explore")
def explore():
    q = request.args.get("q", default="? ? ?")
    edges = query(*q.split(" "))
    node_names = set()
    for e in edges:
        node_names.add(e.o.name)
        node_names.add(e.p.name)
        node_names.add(e.s.name)
    return render_template(
        "graph_explorer.html",
        node_names=node_names,
        edges=edges,
        generate_csrf=generate_csrf,
    )


@graph_bp.route("/json")
def to_json():
    return serialize()

class AddAction:
    pass

class AddNodeAction(AddAction):
    def __init__(self, name, data=None, override=False):
        self.name = name
        self.data = data
        self.override = override

    def __repr__(self):
        data_appendix = f" = { self.data } ({ type(self.data).__name__ })" if self.data is not None else ""
        return f"add_node { self.name }{ data_appendix }"

    def eval(self) -> Node:
        current_app.logger.info(f"eval { self }")
        if self.name in NAME_TO_OBJECT:
            original = NAME_TO_OBJECT.get(self.name)
            assert type(original) == Node
            if self.data and self.data != original.data:
                if self.override:
                    current_app.logger.info(f"overriding data of { self.name }")
                    current_app.logger.info(f"    { original.data } -> { self.data }")
                    original.data = self.data
                else:
                    raise ValueError("failed to override node data")
            return original
        else:
            return add_node(self.name, self.data)

class AddEdgeAction(AddAction):
    def __init__(self, o, p, s, name=None):
        self.o = o
        self.p = p
        self.s = s
        self.name = name

    def __repr__(self):
        return f"add_edge {self.o} {self.p} {self.s}"

    def eval(self) -> Edge:
        o, p, s = list(map(get_or_create, [self.o, self.p, self.s]))
        return add_edge(o, p, s, self.name)


def parse_addition_block(text):
    actions = []

    # CHUNKIZE
    if "\r" in text:
        linebreak = "\r\n"
    else:
        linebreak = "\n"
    lines = text.split(linebreak)
    chunk = []
    chunks = []
    for line in lines:
        if line == "":
            if chunk:
                chunks.append(chunk)
                chunk = []
        else:
            chunk.append(line)
    if chunk:
        chunks.append(chunk)
    print(chunks)

    # PROCESS A CHUNK
    for chunk in chunks:
        head = chunk[0]
        assert head != ""
        assert head[0] != " "

        # HEAD
        it = None  # block object
        instance = False
        if head.startswith("a "):
            head = head[2:]
            instance = True
        if head.startswith("an "):
            head = head[3:]
            instance = True
        words = head.split(" ")
        if instance:
            assert len(words) in (1, 2)
            class_ = words[0]
            assert class_.isidentifier()
            if len(words) == 1:
                instance_name = class_ + "_{uid}"
            else:
                instance_name = words[1]
                assert instance_name.isidentifier()
            it = instance_name
            actions.append(AddEdgeAction(it, "class", class_))
        else:
            it = words[0]
            if "  " in head:
                data = head[len(it):]
                if it[-1] == "!":
                    it = it[:-1]
                    override = True
                else:
                    override = False
                actions.append(AddNodeAction(it, data, override))
            else:
                assert len(words) == 1
                actions.append(AddNodeAction(it))

        # ATTRIBUTES
        for line in chunk[1:]:
            words = line.split(" ")
            if "  " in line:
                pred = words[0]
                assert pred.isidentifier()
                data = line[len(pred)+2:]
                subj = "str_{uid}"
                actions.append(AddNodeAction(subj, data))
                actions.append(AddEdgeAction(it, pred, subj))
            elif len(words) == 2:
                pred = words[0]
                subj = words[1]
                actions.append(AddEdgeAction(it, pred, subj))
                subj = words[0]
            elif len(words) == 1:
                subj = words[0]
                if subj[0] == "#":
                    subj = subj[1:]
                    actions.append(AddEdgeAction(it, "labeled", subj))
                elif subj[0] == "~":
                    subj = subj[1:]
                    actions.append(AddEdgeAction(it, "rel", subj))
                    actions.append(AddEdgeAction(subj, "class", "person"))
                else:         
                    assert subj.isidentifier()
                    actions.append(AddEdgeAction(it, "rel", subj))

    return actions

from .keep import keep
from .label import labels_of
@graph_bp.route("/load_keep")
def load_keep():
    current_app.logger.info("loading keep to explorer")
    notes = keep.all()
    limit = request.args.get("limit")
    if limit:
        notes = notes[:limit]
    current_app.logger.info(f"{ len(notes) } notes detected")
    for note in notes:
        it = add_node("note_{uid}")
        for label in labels_of(note):
            if label.isidentifier():
                add_edge(it, get_or_create("labeled"), get_or_create(label))
            else:
                current_app.logger.warning(f"invalid label detected: \"{ label }\"")
        add_edge(it, get_or_create("title"), add_node(None, note.title))
        add_edge(it, get_or_create("text"), add_node(None, note.text))
    save_inner()
    message = f"success: { len(notes) } notes loaded"
    current_app.logger.info(message)
    return message


import os, shutil


@graph_bp.route("/obsidianize")
def obsidianize():
    current_app.logger.info(f"obsidianizing { len(OBJECTS) } objects")
    folder = config.cache_path + "/obsidian"
    clear_forder(folder)
    nodes_count = 0
    for obj in OBJECTS:
        if type(obj) is Node:
            attr = False
            for edge in obj.sof:
                if edge.p.name in ("text", "title"):
                    attr = True
            if attr:
                continue

            nodes_count += 1
            with open(f"{ folder }/{ obj.name }.md", "w") as f:
                try:
                    f.write("# " + obj.title.data + "\n\n")
                except:
                    pass
                try:
                    f.write(obj.text.data)
                except:
                    pass
                for edge in obj.oof:
                    if edge.p.name in ("text", "title"):
                        continue
                    f.write(f"\n{ edge.p.name } [[{ edge.s.name }]]")

    message = f"success: { nodes_count } obsidian records created"
    current_app.logger.info(message)
    return message


def clear_forder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))