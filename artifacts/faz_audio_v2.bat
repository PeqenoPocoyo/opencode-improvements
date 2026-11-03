@echo off
ffmpeg -y -i RDO_10_barras_de_ouro.mp4 -f lavfi -i "aevalsrc='0.55*sin(2*PI*55*t)*exp(-12*mod(t,0.5)) + 0.25*(2*random(0)-1)*exp(-25*mod(t+0.25,0.5)) + 0.14*(2*random(0)-1)*exp(-80*mod(t+0.125,0.25)) + 0.22*sin(2*PI*41.2*t)*exp(-2*mod(t,0.5))':s=44100:d=19.4" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 128k -shortest RDO_final_com_audio.mp4
