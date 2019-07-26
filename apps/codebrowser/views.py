#coding=utf-8
from uliweb import expose, functions, settings
import os
import time
import logging

log = logging.getLogger('code')

@expose('/codebrowser')
class CodeBrowser(object):
    def __begin__(self):
        self.project_root = os.path.abspath(settings.CODEINSIGHT.project_root)

    @expose('')
    def index(self):
        return {"tdata_json":json_dumps(self._get_tdata(self.project_root))}

    @expose('p',defaults={"path":None})
    @expose('p/<path:path>')
    def project(self,path):
        project_root = self.project_root
        is_root = False
        if path == None:
            path = project_root
            is_root = True
        path = os.path.join(project_root,path)
        path = os.path.normpath(path)
        path_is_file = os.path.isfile(path)
        
        rpath = os.path.normpath(os.path.relpath(path,project_root))
        if rpath == ".":
            rpath = ""
        path_items = self._get_path_items(rpath)

        if path_is_file:
            
            return {
                "path_is_file":path_is_file,
                "path": rpath,
                "path_items_json": json_dumps(path_items)
            }
        else:
            return {
                "path_is_file":path_is_file,
                "path": rpath,
                "tdata_json":json_dumps(self._get_tdata(path,is_root)),
                "path_items_json": json_dumps(path_items)
            }
    def _get_tdata(self,path,is_root=False):
        tdata = []
        ignore_set = set(settings.CODEINSIGHT.entry_name_ignore)
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.name.lower() in ignore_set:
                    continue
                is_file = entry.is_file()
                if is_root:
                    if is_file:
                        break
                    name = "🗄️ " + entry.name
                else:
                    name = ("📄 " if is_file else "📁 ") + entry.name
                st = entry.stat()
                size = st.st_size if is_file else ""
                date_str = time.strftime("%Y-%m-%d",time.localtime(st.st_mtime))
                epath = os.path.relpath(entry.path,self.project_root)
                epath = os.path.normpath(epath)
                d = {"name":name,"date":st.st_mtime,"date_str":date_str,"size":size,"path":epath}
                tdata.append(d)
        tdata.sort(key=lambda i:i["name"])
        return tdata

    def _get_path_items(self,rpath):
        path_items = [{"name":"projects","link":"/"}]
        l = []
        for i in rpath.split(os.sep):
            if i=="":
                break
            l.append(i)
            path_items.append({"name":i,"link":os.sep.join(l)})
        path_items[-1]["active"] = True
        return path_items

    def api_filetext(self):
        path = request.values.get("path")
        if not path:
            return ""
        path = os.path.normpath(path)
        path = os.path.join(self.project_root,path)
        if not os.path.isfile(path):
            return ""
        try:
            return open(path).read()
        except Exception as e:
            log.error(e)
            return ""
