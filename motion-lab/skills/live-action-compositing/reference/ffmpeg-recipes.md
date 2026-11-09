# ffmpeg recipes for compositing (all stdlib ffmpeg; test them on a 3 s clip first)

```bash
# overlay with alpha (ProRes 4444 / WebM VP9 alpha)
ffmpeg -i clip.norm.mp4 -i overlay.mov -filter_complex "[0][1]overlay=format=auto,format=yuv420p" -map 0:a? -c:a copy comp.mp4
# overlay starting at t=2.4 s
ffmpeg -i clip.mp4 -itsoffset 2.4 -i overlay.mov -filter_complex "[0][1]overlay=eof_action=pass" comp.mp4
# crop landscape to vertical 9:16 around x-center (follow subject at x=0.4 of the width)
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih:(iw-ih*9/16)*0.4:0,scale=1080:1920" out.mp4
# blurred-background fit (landscape in vertical)
ffmpeg -i in.mp4 -filter_complex "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3[b];[0]scale=1080:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2" out.mp4
# punch-in zoom 1.0 -> 1.08 between 3.0 s and 3.3 s, hold
ffmpeg -i in.mp4 -vf "zoompan=z='if(between(it,3.0,3.3),1+0.08*(it-3.0)/0.3,if(gte(it,3.3),1.08,1))':d=1:s=1080x1920:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'" out.mp4
# speed ramp: 1.0x then 0.5x between 4 and 5 s
ffmpeg -i in.mp4 -filter_complex "[0]trim=0:4,setpts=PTS-STARTPTS[a];[0]trim=4:5,setpts=2*(PTS-STARTPTS)[b];[0]trim=5,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0" out.mp4
# add film grain to final (match measured sigma: noise strength ~ sigma*255*1.2)
ffmpeg -i comp.mp4 -vf "noise=alls=8:allf=t+u" out.mp4
# duck music under dialogue (sidechain)
ffmpeg -i dialog.wav -i music.wav -filter_complex "[1][0]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[m];[0][m]amix=inputs=2:normalize=0" out.wav
```
