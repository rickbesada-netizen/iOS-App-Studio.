import json, os, re, subprocess, threading, queue, urllib.request, urllib.error, webbrowser, tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

HOME=Path(os.getenv("LOCALAPPDATA",str(Path.home())))/"iOS App Studio"
HOME.mkdir(parents=True,exist_ok=True)
DB=HOME/"projects.json"
BG="#101522"; PANEL="#1b2334"; FG="#edf2ff"; MUTED="#9baac4"; ACC="#7565e9"

def load():
    try: return json.loads(DB.read_text(encoding="utf-8"))
    except (OSError,ValueError): return []
def save(data):
    tmp=DB.with_suffix(".tmp"); tmp.write_text(json.dumps(data,indent=2),encoding="utf-8"); tmp.replace(DB)
def request(url,token,method="GET",data=None):
    headers={"Accept":"application/vnd.github+json","User-Agent":"iOS-App-Studio","Authorization":"Bearer "+token,"X-GitHub-Api-Version":"2022-11-28"}
    if data is not None: headers["Content-Type"]="application/json"
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers,method=method,data=json.dumps(data).encode() if data is not None else None),timeout=40) as r:
        raw=r.read(); return json.loads(raw) if raw else {}
def dart_string(s): return json.dumps(s,ensure_ascii=False).replace("$",r"\$")
def source(p):
    screens=p.get("screens",[]) or [{"title":"Home","body":"Welcome"}]
    entries=",\n".join("("+dart_string(s["title"])+", "+dart_string(s["body"])+")" for s in screens)
    return """import 'package:flutter/material.dart';
void main() => runApp(const MyApp());
class MyApp extends StatelessWidget {
 const MyApp({super.key});
 @override Widget build(BuildContext context) => MaterialApp(
 title: %s, debugShowCheckedModeBanner:false,
 theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff7565e9)),useMaterial3:true),
 home: const Home());
}
class Home extends StatefulWidget {
 const Home({super.key});
 @override State<Home> createState()=>_HomeState();
}
class _HomeState extends State<Home>{
 int index=0;
 final screens=[%s];
 @override Widget build(BuildContext context)=>Scaffold(
 appBar:AppBar(title:Text(screens[index].$1)),
 body:Center(child:Padding(padding:const EdgeInsets.all(24),child:Text(screens[index].$2,style:const TextStyle(fontSize:22)))),
 bottomNavigationBar:screens.length<2?null:NavigationBar(selectedIndex:index,onDestinationSelected:(i)=>setState(()=>index=i),destinations:[for(final s in screens) NavigationDestination(icon:const Icon(Icons.apps),label:s.$1)]));
}
"""%(dart_string(p["name"]),entries)
def project_files(p):
    name=p["slug"]; bundle=p["bundle"]; org=bundle.rsplit(".",1)[0]
    workflow="""name: iOS cloud build
on:
  workflow_dispatch:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  ios:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          channel: stable
      - run: flutter create --platforms=ios --project-name %s --org %s .
      - run: python3 configure_ios.py
      - run: flutter pub get
      - run: flutter analyze
      - run: flutter build ios --release --no-codesign
      - uses: actions/upload-artifact@v4
        with:
          name: unsigned-ios
          path: build/ios/iphoneos/Runner.app
"""%(name,org)
    config="""from pathlib import Path
import re, plistlib
p=Path('ios/Runner.xcodeproj/project.pbxproj')
s=p.read_text()
s=re.sub(r'(PRODUCT_BUNDLE_IDENTIFIER\\s*=\\s*)[^;]+;',lambda m:m.group(1)+%r+';',s)
p.write_text(s)
p=Path('ios/Runner/Info.plist')
d=plistlib.loads(p.read_bytes())
d['CFBundleDisplayName']=%r
p.write_bytes(plistlib.dumps(d))
"""%(bundle,p["name"])
    cm="""workflows:
  ios-testflight:
    name: Signed TestFlight build
    instance_type: mac_mini_m2
    integrations:
      app_store_connect: apple-app-store
    environment:
      flutter: stable
      xcode: latest
      ios_signing:
        distribution_type: app_store
        bundle_identifier: %s
    scripts:
      - script: flutter create --platforms=ios --project-name %s --org %s .
      - script: python3 configure_ios.py
      - script: flutter pub get
      - script: xcode-project use-profiles
      - script: flutter build ipa --release --build-number=$PROJECT_BUILD_NUMBER --export-options-plist=/Users/builder/export_options.plist
    artifacts:
      - build/ios/ipa/*.ipa
    publishing:
      app_store_connect:
        auth: integration
        submit_to_testflight: true
"""%(bundle,name,org)
    return {"pubspec.yaml":f"name: {name}\npublish_to: none\nversion: {p['version']}+1\nenvironment:\n  sdk: '>=3.5.0 <4.0.0'\ndependencies:\n  flutter:\n    sdk: flutter\nflutter:\n  uses-material-design: true\n","lib/main.dart":p.get("code") or source(p),"configure_ios.py":config,".github/workflows/ios.yml":workflow,"codemagic.yaml":cm,".gitignore":".dart_tool/\nbuild/\nios/\n*.p8\n*.p12\n*.mobileprovision\n","README.md":"# "+p["name"]+"\nUnsigned GitHub builds are not installable. Connect Codemagic and Apple signing for TestFlight.\n"}

class Studio(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("iOS App Studio"); self.geometry("1180x780"); self.minsize(900,650); self.configure(bg=BG)
        self.projects=load(); self.current=None; self.token=""; self.events=queue.Queue()
        style=ttk.Style(self); style.theme_use("clam"); style.configure(".",background=PANEL,foreground=FG,fieldbackground=BG,font=("Segoe UI",11)); style.configure("TButton",padding=8); style.map("TButton",background=[("active",ACC)]); style.configure("TEntry",fieldbackground=BG,foreground=FG); style.configure("TNotebook",background=BG); style.configure("TNotebook.Tab",padding=(14,9))
        sidebar=tk.Frame(self,bg=PANEL,width=250); sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar,text="iOS APP STUDIO",bg=PANEL,fg=FG,font=("Segoe UI",17,"bold")).pack(pady=(24,4))
        tk.Label(sidebar,text="Windows • Cloud iOS builds",bg=PANEL,fg=MUTED).pack(pady=(0,20))
        ttk.Button(sidebar,text="+ New application",command=self.new).pack(fill="x",padx=16,pady=5)
        self.list=tk.Listbox(sidebar,bg=BG,fg=FG,selectbackground=ACC,relief="flat",font=("Segoe UI",12),exportselection=False); self.list.pack(fill="both",expand=True,padx=12,pady=12); self.list.bind("<<ListboxSelect>>",self.select)
        ttk.Button(sidebar,text="GitHub connection",command=self.connect).pack(fill="x",padx=16,pady=6)
        ttk.Button(sidebar,text="Open project folder",command=lambda:os.startfile(HOME)).pack(fill="x",padx=16,pady=(0,20))
        self.main=tk.Frame(self,bg=BG); self.main.pack(side="left",fill="both",expand=True,padx=24,pady=20)
        self.title_label=tk.Label(self.main,text="Create your first application",bg=BG,fg=FG,font=("Segoe UI",24,"bold")); self.title_label.pack(anchor="w")
        self.status=tk.StringVar(value="Ready • GitHub token is kept only in memory")
        tk.Label(self.main,textvariable=self.status,bg=BG,fg=MUTED,wraplength=850).pack(anchor="w",pady=8)
        self.tabs=ttk.Notebook(self.main); self.tabs.pack(fill="both",expand=True)
        self.details=ttk.Frame(self.tabs); self.design=ttk.Frame(self.tabs); self.editor=ttk.Frame(self.tabs); self.builds=ttk.Frame(self.tabs)
        for frame,label in [(self.details,"Project"),(self.design,"Screen designer"),(self.editor,"Source code"),(self.builds,"Cloud builds")]: self.tabs.add(frame,text=label)
        self.fields={}
        for key,label in [("name","App display name"),("slug","Flutter project name"),("bundle","Apple bundle ID"),("version","Version"),("repo","GitHub repository (owner/name)")]:
            ttk.Label(self.details,text=label).pack(anchor="w",padx=20,pady=(12,3)); e=ttk.Entry(self.details); e.pack(fill="x",padx=20); self.fields[key]=e
        ttk.Button(self.details,text="Save project",command=self.persist).pack(anchor="w",padx=20,pady=16)
        ttk.Button(self.details,text="Export Flutter project",command=self.export).pack(anchor="w",padx=20)
        self.screenlist=tk.Listbox(self.design,bg=BG,fg=FG,selectbackground=ACC,height=6,exportselection=False); self.screenlist.pack(fill="x",padx=15,pady=12); self.screenlist.bind("<<ListboxSelect>>",self.screen_select)
        self.stitle=ttk.Entry(self.design); self.stitle.pack(fill="x",padx=15,pady=4)
        self.sbody=tk.Text(self.design,height=4,bg=BG,fg=FG,insertbackground=FG); self.sbody.pack(fill="x",padx=15,pady=4)
        bar=ttk.Frame(self.design); bar.pack(fill="x",padx=15)
        for label,cmd in [("Add screen",self.add_screen),("Update screen",self.update_screen),("Remove screen",self.remove_screen),("Preview",self.preview),("Generate Dart",self.generate)]: ttk.Button(bar,text=label,command=cmd).pack(side="left",padx=3,pady=8)
        self.code=tk.Text(self.editor,bg=BG,fg=FG,insertbackground=FG,font=("Consolas",11),undo=True); self.code.pack(fill="both",expand=True,padx=12,pady=12)
        ttk.Button(self.editor,text="Save source",command=self.persist).pack(anchor="w",padx=12,pady=5)
        for label,cmd in [("Push project to GitHub",self.push),("Start unsigned iOS build",self.dispatch),("Refresh build status",self.refresh_runs),("Open GitHub Actions",lambda:self.open_url("actions")),("Open Codemagic",lambda:webbrowser.open("https://codemagic.io/apps")),("Open App Store Connect",lambda:webbrowser.open("https://appstoreconnect.apple.com"))]:
            ttk.Button(self.builds,text=label,command=cmd).pack(anchor="w",padx=15,pady=4)
        self.log=tk.Text(self.builds,bg=BG,fg=FG,height=12,font=("Consolas",10)); self.log.pack(fill="both",expand=True,padx=15,pady=8)
        self.reload(); self.after(100,self.poll)
    def reload(self):
        self.list.delete(0,"end")
        for p in self.projects:self.list.insert("end",p["name"])
    def new(self):
        from tkinter.simpledialog import askstring
        name=askstring("New application","Application name:",parent=self)
        if not name:return
        slug=re.sub(r"[^a-z0-9]+","_",name.lower()).strip("_") or "my_app"
        if not slug[0].isalpha():slug="app_"+slug
        p={"name":name,"slug":slug,"bundle":"com.example."+slug.replace("_",""),"version":"1.0.0","repo":"","screens":[{"title":"Home","body":"Welcome to "+name}]}
        p["code"]=source(p); self.projects.append(p); save(self.projects); self.reload(); self.list.selection_set(len(self.projects)-1); self.select()
    def select(self,event=None):
        s=self.list.curselection()
        if not s:return
        self.current=self.projects[s[0]]
        for k,e in self.fields.items():e.delete(0,"end"); e.insert(0,self.current.get(k,""))
        self.title_label.config(text=self.current["name"]); self.code.delete("1.0","end"); self.code.insert("1.0",self.current.get("code") or source(self.current)); self.reload_screens()
    def persist(self):
        if not self.current:return False
        values={k:e.get().strip() for k,e in self.fields.items()}
        if not values["name"] or not re.fullmatch("[a-z][a-z0-9_]*",values["slug"]) or not re.fullmatch(r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+",values["bundle"]) or not re.fullmatch(r"\d+\.\d+\.\d+",values["version"]):
            messagebox.showerror("Invalid project","Enter a name, valid Flutter project name, reverse-DNS bundle ID and version x.y.z.");return False
        self.current.update(values); self.current["code"]=self.code.get("1.0","end-1c"); save(self.projects); self.title_label.config(text=values["name"]); self.status.set("Project saved"); return True
    def reload_screens(self):
        self.screenlist.delete(0,"end")
        for s in self.current["screens"]:self.screenlist.insert("end",s["title"])
        self.stitle.delete(0,"end"); self.sbody.delete("1.0","end")
    def screen_select(self,event=None):
        sel=self.screenlist.curselection()
        if not sel or not self.current:return
        s=self.current["screens"][sel[0]]; self.stitle.delete(0,"end");self.stitle.insert(0,s["title"]);self.sbody.delete("1.0","end");self.sbody.insert("1.0",s["body"])
    def screen_value(self):return {"title":self.stitle.get().strip() or "Screen","body":self.sbody.get("1.0","end-1c")}
    def add_screen(self):
        if not self.current:return
        if len(self.current["screens"])>=5:messagebox.showinfo("Limit","This starter supports up to five navigation screens.");return
        self.current["screens"].append(self.screen_value());save(self.projects);self.reload_screens()
    def update_screen(self):
        s=self.screenlist.curselection()
        if s and self.current:self.current["screens"][s[0]]=self.screen_value();save(self.projects);self.reload_screens()
    def remove_screen(self):
        s=self.screenlist.curselection()
        if s and self.current and len(self.current["screens"])>1:del self.current["screens"][s[0]];save(self.projects);self.reload_screens()
    def generate(self):
        if self.current and messagebox.askyesno("Generate source","Replace current Dart source with the screen designer output?"):
            self.code.delete("1.0","end");self.code.insert("1.0",source(self.current));self.persist()
    def preview(self):
        if not self.current:return
        w=tk.Toplevel(self);w.title("Layout preview (not iOS simulator)");w.geometry("350x650");w.configure(bg="#f3f2ff")
        title=tk.Label(w,bg="#f3f2ff",fg="#202033",font=("Segoe UI",20,"bold"));title.pack(pady=25)
        body=tk.Label(w,bg="#f3f2ff",fg="#202033",wraplength=280,font=("Segoe UI",17));body.pack(expand=True)
        def show(s):title.config(text=s["title"]);body.config(text=s["body"])
        for s in self.current["screens"]:ttk.Button(w,text=s["title"],command=lambda s=s:show(s)).pack(side="bottom",fill="x")
        show(self.current["screens"][0])
    def export(self):
        if not self.persist():return
        base=filedialog.askdirectory()
        if not base:return
        folder=Path(base)/self.current["slug"]
        if folder.exists() and any(folder.iterdir()):messagebox.showerror("Export","Choose a location without an existing project folder.");return
        for name,content in project_files(self.current).items():
            path=folder/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding="utf-8")
        self.status.set("Exported "+str(folder));os.startfile(folder)
    def connect(self):
        from tkinter.simpledialog import askstring
        token=askstring("GitHub connection","GitHub token with repository Contents and Actions write access (Workflows permission for workflow files). Kept in memory only.",show="*",parent=self)
        if token:self.token=token;self.status.set("GitHub token set for this session")
    def job(self,fn):
        def run():
            try:self.events.put(("ok",fn()))
            except Exception as e:self.events.put(("error",str(e)))
        threading.Thread(target=run,daemon=True).start();self.status.set("Working...")
    def poll(self):
        try:
            while True:
                kind,msg=self.events.get_nowait();self.log.insert("end",str(msg)+"\n");self.log.see("end");self.status.set("Completed" if kind=="ok" else "Error — see build log")
        except queue.Empty:pass
        self.after(100,self.poll)
    def repo(self):
        if not self.persist():return None
        repo=self.current["repo"]
        if not re.fullmatch(r"[\w.-]+/[\w.-]+",repo):messagebox.showerror("Repository","Enter an existing GitHub repository as owner/name.");return None
        if not self.token:self.connect()
        return repo if self.token else None
    def push(self):
        repo=self.repo()
        if not repo:return
        if not messagebox.askyesno("Push","Create or replace generated project files in "+repo+"? Existing unrelated files are preserved."):return
        files=project_files(self.current.copy());token=self.token
        def work():
            import base64
            root="https://api.github.com/repos/"+repo
            meta=request(root,token);branch=meta.get("default_branch") or "main"
            for path,content in files.items():
                url=root+"/contents/"+path;payload={"message":"Update "+path+" from iOS App Studio","content":base64.b64encode(content.encode()).decode(),"branch":branch}
                try:payload["sha"]=request(url+"?ref="+branch,token)["sha"]
                except urllib.error.HTTPError as e:
                    if e.code!=404:raise
                request(url,token,"PUT",payload)
            return "Pushed "+str(len(files))+" files to "+repo
        self.job(work)
    def dispatch(self):
        repo=self.repo()
        if not repo:return
        token=self.token
        def work():
            root="https://api.github.com/repos/"+repo;branch=request(root,token)["default_branch"]
            request(root+"/actions/workflows/ios.yml/dispatches",token,"POST",{"ref":branch});return "Build requested. Refresh status shortly."
        self.job(work)
    def refresh_runs(self):
        repo=self.repo()
        if not repo:return
        token=self.token
        def work():
            runs=request("https://api.github.com/repos/"+repo+"/actions/runs?per_page=10",token).get("workflow_runs",[])
            return "\n".join(f"{r['name']}: {r['status']} / {r.get('conclusion') or '-'}\n{r['html_url']}" for r in runs) or "No builds yet."
        self.job(work)
    def open_url(self,suffix):
        if self.current and self.persist() and re.fullmatch(r"[\w.-]+/[\w.-]+",self.current["repo"]):webbrowser.open("https://github.com/"+self.current["repo"]+"/"+suffix)


class ProStudio(Studio):
    def __init__(self):
        super().__init__()
        self.title("iOS App Studio Pro")
        self.visual=ttk.Frame(self.tabs); self.tabs.add(self.visual,text="Visual canvas")
        self.ai=ttk.Frame(self.tabs); self.tabs.add(self.ai,text="AI builder")
        self.nodes=[]; self.selected_node=None; self.drag=None
        toolbar=ttk.Frame(self.visual); toolbar.pack(fill="x",pady=8)
        for kind in ["Text","Button","Input","Card","Image placeholder"]:
            ttk.Button(toolbar,text="+ "+kind,command=lambda k=kind:self.add_node(k)).pack(side="left",padx=3)
        ttk.Button(toolbar,text="Delete",command=self.delete_node).pack(side="left",padx=3)
        body=ttk.Frame(self.visual); body.pack(fill="both",expand=True)
        self.canvas=tk.Canvas(body,width=320,height=520,bg="#f5f5ff",highlightthickness=0);self.canvas.pack(side="left",padx=16,pady=8)
        self.canvas.bind("<ButtonPress-1>",self.pick);self.canvas.bind("<B1-Motion>",self.move);self.canvas.bind("<ButtonRelease-1>",self.release)
        panel=ttk.Frame(body);panel.pack(side="left",fill="both",expand=True,padx=8)
        self.props={}
        for key,label in [("text","Text / placeholder"),("x","X position"),("y","Y position"),("w","Width"),("h","Height")]:
            ttk.Label(panel,text=label).pack(anchor="w",pady=(8,2)); e=ttk.Entry(panel);e.pack(fill="x");self.props[key]=e
        ttk.Button(panel,text="Apply properties",command=self.apply_props).pack(fill="x",pady=10)
        ttk.Button(panel,text="Generate Flutter layout",command=self.canvas_code).pack(fill="x",pady=4)
        ttk.Label(panel,text="Drag components on the canvas.\\nLayout uses proportional positioning.",wraplength=240).pack(anchor="w",pady=8)
        self.model=ttk.Entry(self.ai); self.model.insert(0,"qwen2.5-coder:7b")
        ttk.Label(self.ai,text="Local Ollama model (must be installed and running)").pack(anchor="w",padx=15,pady=(12,4));self.model.pack(fill="x",padx=15)
        ttk.Label(self.ai,text="Describe the app or changes you want").pack(anchor="w",padx=15,pady=8)
        self.prompt=tk.Text(self.ai,height=8,bg=BG,fg=FG,insertbackground=FG);self.prompt.pack(fill="x",padx=15)
        ttk.Button(self.ai,text="Generate Dart with local AI",command=self.ai_generate).pack(anchor="w",padx=15,pady=10)
        self.ai_result=tk.Text(self.ai,bg=BG,fg=FG,insertbackground=FG,font=("Consolas",10));self.ai_result.pack(fill="both",expand=True,padx=15,pady=5)
        ttk.Button(self.ai,text="Apply generated code to project",command=self.apply_ai).pack(anchor="w",padx=15,pady=8)
        self.ai_events=queue.Queue();self.after(150,self.poll_ai)
    def select(self,event=None):
        super().select(event)
        if self.current and hasattr(self,"canvas"):
            self.nodes=self.current.setdefault("nodes",[]);self.selected_node=None;self.redraw()
    def add_node(self,kind):
        if not self.current:return
        self.nodes.append({"kind":kind,"text":kind,"x":20,"y":min(450,20+len(self.nodes)*55),"w":220,"h":48})
        self.selected_node=len(self.nodes)-1;self.sync()
    def sync(self):
        if self.current:self.current["nodes"]=self.nodes;save(self.projects)
        self.redraw()
        if self.selected_node is not None:
            for k,e in self.props.items():e.delete(0,"end");e.insert(0,str(self.nodes[self.selected_node][k]))
    def redraw(self):
        self.canvas.delete("all")
        for i,n in enumerate(self.nodes):
            x,y,w,h=[n[k] for k in ("x","y","w","h")]
            fill={"Button":"#7565e9","Input":"#ffffff","Card":"#dedcf5","Image placeholder":"#ccd2e5","Text":"#f5f5ff"}[n["kind"]]
            tag="node"+str(i)
            self.canvas.create_rectangle(x,y,x+w,y+h,fill=fill,outline="#7565e9" if i==self.selected_node else "#b7bbce",width=2 if i==self.selected_node else 1,tags=(tag,))
            self.canvas.create_text(x+w/2,y+h/2,text=n["text"],width=max(10,w-8),fill="white" if n["kind"]=="Button" else "#202033",tags=(tag,))
    def pick(self,e):
        hits=self.canvas.find_overlapping(e.x,e.y,e.x,e.y)
        if not hits:return
        tags=self.canvas.gettags(hits[-1])
        for tag in tags:
            if tag.startswith("node"):
                self.selected_node=int(tag[4:]);n=self.nodes[self.selected_node];self.drag=(e.x-n["x"],e.y-n["y"]);self.sync();break
    def move(self,e):
        if self.drag is None or self.selected_node is None:return
        n=self.nodes[self.selected_node];n["x"]=max(0,min(320-n["w"],e.x-self.drag[0]));n["y"]=max(0,min(520-n["h"],e.y-self.drag[1]));self.redraw()
    def release(self,e):
        if self.drag is not None:self.drag=None;self.sync()
    def delete_node(self):
        if self.selected_node is not None:del self.nodes[self.selected_node];self.selected_node=None;self.sync()
    def apply_props(self):
        if self.selected_node is None:return
        try:
            n=self.nodes[self.selected_node];w=max(20,min(320,int(self.props["w"].get())));h=max(20,min(520,int(self.props["h"].get())))
            n.update(text=self.props["text"].get(),w=w,h=h,x=max(0,min(320-w,int(self.props["x"].get()))),y=max(0,min(520-h,int(self.props["y"].get()))));self.sync()
        except ValueError:messagebox.showerror("Properties","Enter whole numbers for dimensions and position.")
    def canvas_code(self):
        if not self.current or not self.nodes:return
        if not messagebox.askyesno("Generate layout","Replace the current Dart source with this canvas?"):return
        widgets=[]
        for n in self.nodes:
            t=dart_string(n["text"]);k=n["kind"]
            child={"Text":f"Center(child:Text({t}))","Button":f"ElevatedButton(onPressed:(){{}},child:Text({t}))","Input":f"TextField(decoration:InputDecoration(labelText:{t},border:const OutlineInputBorder()))","Card":f"Card(child:Center(child:Text({t})))","Image placeholder":"const ColoredBox(color:Colors.black12,child:Icon(Icons.image))"}[k]
            widgets.append(f"Positioned(left:c.maxWidth*{n['x']/320:.6f},top:c.maxHeight*{n['y']/520:.6f},width:c.maxWidth*{n['w']/320:.6f},height:c.maxHeight*{n['h']/520:.6f},child:{child})")
        code="import 'package:flutter/material.dart';\nvoid main()=>runApp(MaterialApp(home:Scaffold(appBar:AppBar(title:Text("+dart_string(self.current["name"])+")),body:SafeArea(child:LayoutBuilder(builder:(context,c)=>Stack(children:[\n"+",\n".join(widgets)+"\n]))))));\n"
        self.code.delete("1.0","end");self.code.insert("1.0",code);self.persist();self.tabs.select(self.editor)
    def ai_generate(self):
        if not self.current:return
        prompt=self.prompt.get("1.0","end-1c").strip();model=self.model.get().strip()
        if not prompt or not model:return
        old=self.code.get("1.0","end-1c")
        self.status.set("Local AI generating...");self.ai_result.delete("1.0","end")
        def work():
            try:
                data={"model":model,"stream":False,"messages":[{"role":"system","content":"Return only a complete Flutter lib/main.dart file. Use Flutter SDK only, no external packages. Do not include markdown. Preserve relevant existing features."},{"role":"user","content":prompt+"\nExisting source:\n"+old}]}
                req=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=json.dumps(data).encode(),headers={"Content-Type":"application/json"})
                with urllib.request.urlopen(req,timeout=600) as r:result=json.load(r)["message"]["content"].strip()
                result=re.sub(r"^"+chr(96)*3+r"(?:dart)?\s*|\s*"+chr(96)*3+r"$","",result)
                self.ai_events.put((True,result))
            except Exception as e:self.ai_events.put((False,str(e)))
        threading.Thread(target=work,daemon=True).start()
    def poll_ai(self):
        try:
            while True:
                ok,result=self.ai_events.get_nowait();self.ai_result.delete("1.0","end");self.ai_result.insert("1.0",result);self.status.set("AI response ready — review before applying" if ok else "AI connection failed — check Ollama and model")
        except queue.Empty:pass
        self.after(150,self.poll_ai)
    def apply_ai(self):
        result=self.ai_result.get("1.0","end-1c")
        if self.current and "void main" in result and messagebox.askyesno("Apply AI code","Replace current Dart source? Review and build-test the generated code."):
            self.code.delete("1.0","end");self.code.insert("1.0",result);self.persist();self.tabs.select(self.editor)

if __name__=="__main__":ProStudio().mainloop()

