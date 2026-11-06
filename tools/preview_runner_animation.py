"""Package Blender-rendered animation frames into GIFs and contact sheets."""
from pathlib import Path
from PIL import Image, ImageDraw

root=Path(__file__).resolve().parents[1]/'art'/'runner'/'animations'
for name in ['Idle','Run','Jump']:
    paths=sorted((root/name).glob('*.png'))
    frames=[Image.open(p).convert('RGB') for p in paths]
    assert frames,name
    frames[0].save(root/(name+'.gif'),save_all=True,append_images=frames[1:],duration=[67,67,66]*(len(frames)//3)+[67]*(len(frames)%3),loop=0 if name!='Jump' else 1)
    indices=[round(i*(len(frames)-1)/5) for i in range(6)]
    sheet=Image.new('RGB',(320*3,430*2),(24,27,32))
    draw=ImageDraw.Draw(sheet)
    for n,i in enumerate(indices):
        x=n%3*320; y=n//3*430
        sheet.paste(frames[i],(x,y))
        draw.text((x+12,y+407),f'{name} - frame {paths[i].stem}',fill='white')
    sheet.save(root/(name+'-contact.png'))
    print(name,len(frames),'frames packaged')
