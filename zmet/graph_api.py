from flask import Blueprint, Response, redirect, url_for, request, current_app, render_template
from flask_wtf.csrf import generate_csrf
from . import zmet_lang
from .graph import graph
from .auth import admin_required
from pyoxigraph import NamedNode, DefaultGraph, QuerySolutions, QueryTriples
import io
import html

graph_bp = Blueprint("graph", __name__, url_prefix="/graph", template_folder="templates")


def get_graph_name():
    graph_name = request.args.get("name")
    if graph_name is not None:
        return NamedNode(graph_name)
    else:
        return DefaultGraph


@graph_bp.route("/flush")
@admin_required
def flush():
    try:
        graph.flush()
        return "graph flushed"
    except Exception as e:
        return str(e)


@graph_bp.route("/optimize")
@admin_required
def optimize():
    try:
        graph.optimize()
        return "graph optimized"
    except Exception as e:
        return str(e)


@graph_bp.route("/as_trig")
@admin_required
def as_trig():
    try:
        out = io.BytesIO()
        graph.dump(out, "application/trig")
        return Response(out.getvalue(), mimetype="application/trig")
    except Exception as e:
        return str(e)


@graph_bp.route("/as_ttl")
@admin_required
def as_ttl():
    try:
        out = io.BytesIO()
        graph.dump(out, "text/turtle")
        return Response(out.getvalue(), mimetype="text/turtle")
    except Exception as e:
        return str(e)


@graph_bp.route("/")
def index():
    return """
    <html>
    <head>
        <style>
            html {
                height: 100%;
                width: 100%;
            }
            body {
              min-width:  100%;
              min-height: 100%;
              margin: 0px;
              padding: 0px;
              display: grid;
              grid-template-columns: 50vw 50vw;
              grid-template-rows: 1fr;
              gap: 0px;
            }
            iframe {
                width: 100%;
                height: 100%;
            }
        </style>
    <body>
        <div id="add_wrapper">
            <iframe id="add_iframe" src="/graph/add" title="add"></iframe>
        </div>
        <div id="query_wrapper">
            <iframe id="query_iframe" src="/graph/query" title="query"></iframe>  
        </div>
    </body>
    </html>
    """


@graph_bp.route("/clear")
@admin_required
def clear():
    try:
        graph_name = get_graph_name()
        graph.clear()
        return f"graph { graph_name } cleared"
    except Exception as e:
        return str(e)

@graph_bp.route("/add", methods=["GET"])
@admin_required
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
@admin_required
def add_post():
    text = request.form.get("text")
    if text is None: return "no text found"
    # parse(text)
    quads = zmet_lang.parse(text)
    current_app.logger.info("== add ==")
    for quad in quads:
        current_app.logger.info(str(quad))
    current_app.logger.info("==  .  ==")
    global TRANSACTION
    TRANSACTION = quads
    return redirect(url_for("graph.transaction_get"))


@graph_bp.route("/transaction", methods=["GET"])
@admin_required
def transaction_get():
    button = f"""
        <form method="post">
          <input type="submit">
          <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
    """
    return "<br />".join(map(lambda x: html.escape(zmet_lang.show(x)), TRANSACTION)) + "<br />" + button


@graph_bp.route("/transaction", methods=["POST"])
@admin_required
def transaction_post():
    try:
        graph.extend(TRANSACTION)
        return "success"
    except Exception as e:
        return str(e)


@graph_bp.route("/query", methods=["GET"])
@admin_required
def search():
    q = request.args.get("q")
    if q is not None:
        try:
            resp = graph.query(
                query=q,
                use_default_graph_as_union=bool(request.args.get("use_default_graph_as_union")),
            )
            if isinstance(resp, QuerySolutions):
                return render_template(
                    "simple_table.html",
                    variables=[var.value for var in resp.variables],
                    data=[{var.value: zmet_lang.show(sol[var]) for var in resp.variables} for sol in resp],
                )
            elif isinstance(resp, bool):
                return str(resp)
            elif isinstance(resp, QueryTriples):
                return str(list(resp))  # TODO
            else:
                raise ValueError
        except Exception as e:
            return str(e)
    return f"""
        <form method="get">
          <textarea rows="10" cols="50" name="q">PREFIX : <{ zmet_lang.zmt.url }>
SELECT ?s ?p ?o {{?s  ?p  ?o }}
</textarea>
          <input type="submit">
          <input type="hidden" name="csrf_token" value="{ generate_csrf() }">
        </form>
    """


@graph_bp.route("/graph_json")
@admin_required
def graph_json():
    objects = []
    nodes = set()
    for s, p, o, _ in graph:
        pass
    return ""



from .keep import keep
from .label import labels_of
@graph_bp.route("/load_keep")
@admin_required
def load_keep():
    return "not implemented"
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
@admin_required
def obsidianize():
    return "not implemented"
    current_app.logger.info(f"obsidianizing { len(graph) } quads")
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