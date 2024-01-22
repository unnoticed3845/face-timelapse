from flask import (
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_file
)
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from pathlib import Path
import logging

from app import app, thread_manager
from src.render_queue import RenderItem

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'zip'}
def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

def est_time_str(sec: float) -> str:
    seconds = max(int(sec), 0)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    result = ""
    if hours: result += f"{hours}h "
    if minutes: result += f"{minutes}m "
    return result + f"{seconds}s"

def mask_string(string: str, to_show: int = 4) -> str:
    return string[0:to_show] + '*' * 4


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/debug')
def debug():
    return [ f"{mask_string(k)}:{v.status}" for k, v in thread_manager.item_index.items() ]

@app.route('/download/<token>')
def download(token):
    if not isinstance(token, str):
        flash("token must be a string", category='error')
        return redirect(url_for(result))
    filename = f"{token}.mp4"
    filename = Path(safe_join(app.config['VID_DIR'], filename)).absolute()
    if not Path(filename).exists():
        flash("invalid token", category='error')
        return redirect(url_for(result))
    return send_file(
        filename,
        as_attachment=True
    )

@app.route('/result/<token>')
def result(token):
    first_time = request.args.get('first_time', None, int)
    if not isinstance(token, str):
        flash("token must be a string", category='error')
        return redirect(url_for('index'))
    
    if token in thread_manager.item_index:
        status = thread_manager.item_index[token].status
    elif Path(app.config['VID_DIR']).joinpath(f"{token}.mp4").exists():
        status = 'Done'
    else:
        flash("Unknown token", category='error')
        return redirect(url_for('index'))

    return render_template(
        'result.html',
        status = status,
        token = token,
        first_time=bool(first_time)
    )

@app.route('/render', methods=['GET', 'POST'])
def render():
    if request.method == 'GET':
        queue_size = thread_manager.queue.qsize()
        avg_time = thread_manager.render_time_history.avg()
        avg_time = avg_time / thread_manager.thread_count

        return render_template(
            'render.html',
            queue_size = queue_size,
            est_render_time = est_time_str(avg_time * queue_size)
        )
    elif request.method == 'POST':
        if 'file' not in request.files:
            flash("No file given", category='error')
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            flash("No file given", category='error')
            return redirect(url_for('index'))
        if not allowed_file(file.filename):
            flash(f"Only {ALLOWED_EXTENSIONS} files supported", category='error')
            return redirect(url_for('index'))
        else:
            item = RenderItem()
            file.save(item.filename)
            thread_manager.add_render_task(item)
            return redirect(url_for('result', token=item.token, first_time=1))

@app.route('/howtouse')
def howtouse():
    return render_template('base.html')
