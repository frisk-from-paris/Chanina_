from chanina.chanina import ChaninaApplication, WorkerContext
from chanina.tools.navigate import goto


app = ChaninaApplication(__name__)
app_celery = app.celery


@app.feature('test')
def test(ctx: WorkerContext, *_, **__):
    ctx.new_page()
    goto("https://google.com", context=ctx)

def main():
    print(app.celery.tasks.get("test"))
    print(app.celery.tasks.get("feature.test"))
    print(app.features)
