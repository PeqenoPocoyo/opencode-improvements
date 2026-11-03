@echo off
ffmpeg -y -v error -stats ^
 -f lavfi -i "gradients=size=1296x2304:rate=30:speed=0.05:type=radial:nb_colors=3:c0=0x050505:c1=0x8a5b1e:c2=0x0b0b0b:x0=648:y0=980:x1=700:y1=1090" ^
 -f lavfi -i "color=c=white:size=1080x1920:rate=30:duration=0.35" ^
 -filter_complex ^
 "[0:v]gblur=sigma=28,eq=contrast=1.14:saturation=1.22:brightness=-0.02,noise=alls=4:allf=t+u,vignette=PI/4,zoompan=z='1.05+0.0004*on':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1[bg];[1:v]fade=t=out:st=0:d=0.35:alpha=1,format=rgba[fl];[bg][fl]overlay=0:0:eof_action=pass[bg2];[bg2]drawtext=fontfile=segoeuil.ttf:text='G U I A   E X P R E S S':fontsize=34:fontcolor=0xC9A24B:x=(w-text_w)/2:y=300:alpha='if(lt(t,0.35),t/0.35,1)',drawtext=fontfile=segoeuib.ttf:text='COMO RESGATAR':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=560:shadowcolor=0x000000@0.7:shadowx=0:shadowy=10,drawbox=x=390:y=700:w=300:h=6:color=0xE8B23A@0.95:enable='gte(t,0.55)',drawtext=fontfile=segoeuib.ttf:text='10 BARRAS':fontsize=128:fontcolor=0xE8B23A:x=(w-text_w)/2:y=780:alpha='if(lt(t,0.5),0,if(lt(t,0.75),(t-0.5)*4,1))':shadowcolor=0x000000@0.7:shadowx=0:shadowy=10,drawtext=fontfile=segoeuib.ttf:text='DE OURO':fontsize=128:fontcolor=0xE8B23A:x=(w-text_w)/2:y=940:alpha='if(lt(t,0.65),0,if(lt(t,0.9),(t-0.65)*4,1))':shadowcolor=0x000000@0.7:shadowx=0:shadowy=10,drawtext=fontfile=segoeuil.ttf:text='TUDO   GRATIS':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=1480:alpha='if(lt(t,0.9),0,if(lt(t,1.2),(t-0.9)*3.33,1))',fade=t=in:st=0:d=0.12,fade=t=out:st=2.7:d=0.3,format=yuv420p[vout]" ^
 -map "[vout]" -c:v libx264 -preset medium -crf 17 -g 30 -r 30 -x264-params keyint=30:min-keyint=30 -t 3.0 s1.mp4
if errorlevel 1 goto fail
echo S1-OK
goto eof
:fail
echo S1-FAIL
:eof
