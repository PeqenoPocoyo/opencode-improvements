@echo off
ffmpeg -y -v error -stats ^
 -f lavfi -i "gradients=size=1296x2304:rate=30:speed=0.05:type=radial:nb_colors=3:c0=0x060606:c1=0x9c6a24:c2=0x040404:x0=560:y0=760:x1=640:y1=880" ^
 -f lavfi -i "color=c=white:size=1080x1920:rate=30:duration=0.35" ^
 -f lavfi -i "color=c=0xC9A24B:size=1080x1920:rate=30" ^
 -f lavfi -i "color=c=0xFFD75E:size=1080x1920:rate=30" ^
 -filter_complex ^
 "[0:v]gblur=sigma=26,eq=contrast=1.12:saturation=1.2:brightness=-0.02,noise=alls=4:allf=t+u,vignette=PI/4,zoompan=z='1.1-0.00035*on':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,setsar=1[bg];[1:v]fade=t=out:st=0:d=0.35:alpha=1,format=rgba[fl];[bg][fl]overlay=0:0:eof_action=pass[bg2];[bg2]drawbox=x=160:y=900:w=760:h=620:color=0x0B0C10@0.88:enable='gte(t,0.4)',drawbox=x=180:y=1060:w=720:h=2:color=white@0.09,drawbox=x=180:y=1200:w=720:h=2:color=white@0.09,drawbox=x=180:y=1340:w=720:h=2:color=white@0.09,drawbox=x=320:y=940:w=2:h=540:color=white@0.09,drawbox=x=520:y=940:w=2:h=540:color=white@0.09,drawbox=x=720:y=940:w=2:h=540:color=white@0.09[bg5];[2:v]format=rgba,geq=a='if(lt(sqrt(pow(X-300,2)+pow(Y-1130,2)),13),255,if(lt(sqrt(pow(X-362,2)+pow(Y-1176,2)),13),255,if(lt(sqrt(pow(X-424,2)+pow(Y-1222,2)),13),255,if(lt(sqrt(pow(X-486,2)+pow(Y-1268,2)),13),255,if(lt(sqrt(pow(X-548,2)+pow(Y-1314,2)),13),255,if(lt(sqrt(pow(X-610,2)+pow(Y-1360,2)),13),255,0))))))':r='r(X,Y)':g='g(X,Y)':b='b(X,Y)',fade=t=in:st=0.5:d=0.3:alpha=1[dots];[3:v]format=rgba,geq=a='if(lt(sqrt(pow(X-672,2)+pow(Y-1405,2)),22),255,if(lt(abs(sqrt(pow(X-672,2)+pow(Y-1405,2))-(34+8*abs(sin(2*PI*T/0.7)))),3),160,0))':r='r(X,Y)':g='g(X,Y)':b='b(X,Y)',fade=t=in:st=1.1:d=0.35:alpha=1[dest];[bg5][dots]overlay=0:0[bg6];[bg6][dest]overlay=0:0[bg7];[bg7]drawbox=x=430:y=400:w=220:h=64:color=0xE8B23A@0.92:enable='gte(t,0.3)',drawtext=fontfile=segoeuib.ttf:text='PASSO   2':fontsize=34:fontcolor=0x101010:x=(w-text_w)/2:y=417:enable='gte(t,0.3)',drawtext=fontfile=segoeuib.ttf:text='MARCA O CAMINHO':fontsize=88:fontcolor=white:x=(w-text_w)/2:y=545:alpha='if(lt(t,0.35),0,if(lt(t,0.6),(t-0.35)*4,1))':shadowcolor=0x000000@0.7:shadowx=0:shadowy=10,drawbox=x=430:y=705:w=220:h=5:color=0xE8B23A@0.95:enable='gte(t,0.55)',drawtext=fontfile=segoeuil.ttf:text='TOQUE NO PONTO DO INIMIGO':fontsize=38:fontcolor=white:x=(w-text_w)/2:y=1680:alpha='if(lt(t,1.25),0,if(lt(t,1.55),(t-1.25)*3.33,1))',fade=t=in:st=0:d=0.12,fade=t=out:st=2.2:d=0.3,format=yuv420p[vout]" ^
 -map "[vout]" -c:v libx264 -preset medium -crf 17 -g 30 -r 30 -x264-params keyint=30:min-keyint=30 -t 2.5 s3.mp4
if errorlevel 1 goto fail
echo S3-OK
goto eof
:fail
echo S3-FAIL
:eof