import sys, certifi, asyncio
certifi.where = lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
from edge_tts import communicate as c
async def main(text, voice, out, words_out, rate):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    import json; words=[]
    with open(out,"wb") as f:
        async for ch in com.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append({"t":ch["offset"]/1e7,"d":ch["duration"]/1e7,"w":ch["text"]})
    json.dump(words, open(words_out,"w"), ensure_ascii=False, indent=0)
text=open(sys.argv[1]).read().strip()
asyncio.run(main(text, sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv)>5 else "+0%"))
