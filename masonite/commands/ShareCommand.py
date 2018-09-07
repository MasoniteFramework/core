from cleo import Command
import shutil
import subprocess


class ShareCommand(Command):
    """
    Strats a ngrok tunnel

    share
        {--port=8000 : Specify which port to run the server}
        {--host=127.0.0.1 : Specify which ip address to run the server}
        {--path=ngrok : Specify which ngrok executable path to run the ngrok}
    """

    def handle(self):
        ngrok = self.option('path')
        port = self.option('port')
        host = self.option('host')

        if shutil.which(ngrok) is not None:
            start_ngrok = subprocess.Popen(
                '{ngrok} http {host}:{port}'.format(ngrok=ngrok, host=host, port=port),
                shell=True)
            subprocess.call(
                'craft serve --port {port} --host {host}'.format(
                    port=port, host=host),
                shell=True)
        else:
            self.error('ngrok: command not found')
