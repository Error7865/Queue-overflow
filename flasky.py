import os
import sys
import click
from flask_migrate import Migrate, upgrade
from app import create_app,db
from app.models import User, Role

COV=None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV=coverage.coverage(branch=True, include='app/*')
    COV.start()

app=create_app(os.environ.get('FLASKY_CONFIG') or 'default')
# from werkzeug.middleware.profiler import ProfilerMiddleware
# app.wsgi_app=ProfilerMiddleware(app.wsgi_app, restrictions=[25], profile_dir=r'C:\Users\Robin\Documents\mydoc')
migrate=Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

@app.cli.command()
# @click.option('--coverage/--no-coverage', default=False, help='Run tests under code coverage.')
def test():
    '''Run the unittest '''
    # if coverage and not os.environ.get('FLASK_COVERAGE'):
    #     os.environ['FLASK_COVERAGE']='1'
    #     os.execvp(sys.executable, [sys.executable]+sys.argv)
    import unittest
    tests=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    # if COV:
    #     COV.stop()
    #     COV.save()
    #     print('Coverage Summary: ')
    #     COV.report()
    #     basedir=os.path.abspath(os.path.dirname(__file__))
    #     # basedir='C:\Users\error\Documents\flask\vir_env\Scripts\flask'
    #     covdir=os.path.join(basedir, 'tmp/coverage')
    #     COV.html_report(directory=covdir)
    #     print(f'HTML version: file://{covdir}/index.html')
    #     COV.erase()

@app.cli.command()
@click.option('--length', default=25, help='Number of function to include the profiler')
@click.option('--profile-dir', default=None, help='Directory where profiler data file will save')
def profile(length, profile_dir):
    '''Start the application under the code compiler'''
    from werkzeug.middleware.profiler import ProfilerMiddleware
    app.wsgi_app=ProfilerMiddleware(app.wsgi_app, restrictions=[length], profile_dir=profile_dir)
    # app.run(debug=False)

@app.cli.command()
def deploy():
    '''Run  deployment tasks'''
    #migrate database to latest version
    upgrade()
    #create or update user
    Role.insert_roles()
    #ensure that all user following themself
    User.add_self_follows()