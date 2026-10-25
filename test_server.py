import json, socket, tempfile, threading, unittest, urllib.error, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
import server as app

class AppSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(dir=ROOT); app.DB=Path(cls.tmp.name)/'test.sqlite3'; app.init_db()
        cls.http=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler); cls.port=cls.http.server_address[1]
        cls.base=f'http://127.0.0.1:{cls.port}'; cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True); cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown(); cls.http.server_close(); cls.thread.join(timeout=3)
        # TemporaryDirectory cleanup can be denied by sandbox ACLs on Windows; keep the
        # test database under the repository's ignored temp folder and let the OS clean it.
        try: cls.tmp.cleanup()
        except PermissionError: pass
    def client(self): return urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    def req(self,client,path,method='GET',body=None):
        data=json.dumps(body).encode() if body is not None else None
        request=urllib.request.Request(self.base+path,data=data,method=method,headers={'Content-Type':'application/json'} if data else {})
        try:
            with client.open(request,timeout=3) as res: return res.status,json.loads(res.read())
        except urllib.error.HTTPError as e:
            code=e.code; payload=json.loads(e.read()); e.close(); return code,payload
    def test_registration_password_and_task_owner_scope(self):
        a,b=self.client(),self.client()
        status,user=self.req(a,'/api/auth/register','POST',{'name':'Ada Student','email':'ada@example.test','password':'secure-passphrase'})
        self.assertEqual(status,200); self.assertEqual(user['user']['role'],'student')
        self.assertEqual(self.req(a,'/api/tasks','POST',{'title':'Review algorithms','priority':'high'})[0],201)
        self.assertEqual(len(self.req(a,'/api/tasks')[1]['tasks']),1)
        self.assertEqual(self.req(b,'/api/tasks')[0],401)
        self.assertEqual(self.req(a,'/api/auth/logout','POST',{})[0],200)
        self.assertEqual(self.req(a,'/api/me')[0],401)
    def test_duplicate_and_invalid_registration_rejected(self):
        a=self.client()
        self.assertEqual(self.req(a,'/api/auth/register','POST',{'name':'A','email':'bad','password':'short'})[0],400)
        self.req(a,'/api/auth/register','POST',{'name':'Lin Student','email':'lin@example.test','password':'long-enough-password'})
        self.assertEqual(self.req(a,'/api/auth/register','POST',{'name':'Lin Student','email':'lin@example.test','password':'long-enough-password'})[0],409)
    def test_health_and_static_app(self):
        self.assertTrue(self.req(self.client(),'/api/health')[1]['ok'])
        with urllib.request.urlopen(self.base+'/',timeout=3) as r: self.assertIn(b'CampusGPT',r.read())

if __name__=='__main__': unittest.main()

