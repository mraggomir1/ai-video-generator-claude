import json, subprocess, re, os, sys
sys.path.insert(0, "..")
VOICE="ru-RU-DmitryNeural"; RATE="+20%"
scenes=[
 ("hook",  "Спорим, твой ИИ|И-И снимет видео круче тебя? Если знает *десять* скиллов."),
 ("slop",  "Пишешь ему «сделай крутое видео» — и получаешь *мыло*."),
 ("engine","Seedance|Сидэнс — точный движок. Ему нужны *секунды*, *камера*, *свет* и *звук*."),
 ("prompt","Эти скиллы для Claude|Клода пишут всё за тебя: одна идея — и готовый промпт на *двадцать* *строк*."),
 ("grid",  "Для *просмотров* — вирусный хук, безликий канал, подкаст. Для *бизнеса* — запуск SaaS|саас, промо курса, отзывы. Для *бренда* — личный бренд, люкс, до-после и ИИ-аватар|И-И-аватар."),
 ("hook2s","А главное — первые *две* *секунды*: уйдут *пятьдесят* процентов зрителей или останутся *девяносто*."),
 ("cta",   "Ставь эти скиллы, кидай идею — забирай готовый промпт. Подпишись, а то кадр *смажется*."),
]
GAP=0.18; LEAD=0.35
out=[]; t=LEAD; parts=[]
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t",str(LEAD),"lead.wav"],check=True)
parts.append("lead.wav")
for i,(sid,text) in enumerate(scenes):
    toks=[]
    for raw in text.split():
        disp,_,tts=raw.partition("|")
        hl = "*" in disp
        disp=disp.replace("*",""); tts=(tts or disp).replace("*","")
        # carry trailing punctuation of disp onto tts
        m=re.search(r"[.,:;!?»]+$",disp)
        if m and not tts.endswith(m.group()): tts+=m.group()
        toks.append({"w":disp,"tts":tts,"hl":hl})
    tts_text=" ".join(x["tts"] for x in toks)
    open(f"s{i}.txt","w").write(tts_text)
    import time
    for a in range(8):
        r=subprocess.run([sys.executable,"tts.py",f"s{i}.txt",VOICE,f"s{i}.mp3",f"s{i}.json",RATE],capture_output=True)
        if r.returncode==0: break
        print("retry",sid); time.sleep(3)
    else: raise SystemExit("tts failed "+sid)
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"s{i}.mp3","-ar","24000","-ac","1",f"s{i}.wav"],check=True)
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"s{i}.wav"]))
    bnd=json.load(open(f"s{i}.json"))
    # align: each display token -> number of spoken words in its tts (ignore pure punctuation tokens)
    words=[x for x in toks if re.search(r"\w",x["w"])]
    nspoken=[len([p for p in re.split(r"[\s\-]+",x["tts"]) if re.search(r"\w",p)]) for x in words]
    if sum(nspoken)==len(bnd):
        k=0
        for x,n in zip(words,nspoken): x["t"]=bnd[k]["t"]; k+=n
    elif len(words)==len(bnd):
        for x,b in zip(words,bnd): x["t"]=b["t"]
    else:
        print("MISMATCH",sid,len(words),sum(nspoken),len(bnd),[b["w"] for b in bnd])
        s=bnd[0]["t"]; e=bnd[-1]["t"]+bnd[-1]["d"]; L=sum(len(x["w"]) for x in words); acc=0
        for x in words: x["t"]=s+(e-s)*acc/L; acc+=len(x["w"])
    for x in toks:
        if "t" not in x: x["t"]=None
    # punctuation-only tokens inherit previous time
    last=0
    for x in toks:
        if x["t"] is None: x["t"]=last
        last=x["t"]; x["t"]=round(x["t"]+t,3); del x["tts"]
    out.append({"id":sid,"start":round(t,3),"end":round(t+dur+GAP,3),"words":toks})
    parts.append(f"s{i}.wav")
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t",str(GAP),f"g{i}.wav"],check=True)
    parts.append(f"g{i}.wav")
    t+=dur+GAP
open("list.txt","w").write("".join(f"file '{p}'\n" for p in parts))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-c","pcm_s16le","voice.wav"],check=True)
json.dump({"duration":round(t+0.8,3),"scenes":out},open("scenes.json","w"),ensure_ascii=False,indent=1)
print("total",t)
