from cmu_graphics import *
import math

def onAppStart(app):
    app.page = "homepage"
    app.width = 1000
    app.height = 1000
    
    # Music setup
    app.music = Sound("https://vgmsite.com/soundtracks/new-super-luigi-u-2019/ztszdhxgsu/01.%20Title%20Theme.mp3")
    app.musicOn = True
    app.music.play(loop=True)

    # 3D world setup
    app.worldMap = [
        [1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,0,0,1,0,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,0,0,1,0,1],
        [1,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1],
    ]
    app.playerX = 1.5
    app.playerY = 1.5
    app.playerAngle = 0
    app.fov = math.pi / 3
    app.rayCount = 100
    app.moveSpeed = 0.1
    app.rotateSpeed = 0.1

def onKeyPress(app, key):
    if key == 'm':
        toggleMusic(app)

def onKeyHold(app, keys):
    if app.page == "mainpage":
        if 'a' in keys:
            app.playerAngle -= app.rotateSpeed
        if 'd' in keys:
            app.playerAngle += app.rotateSpeed
        if 'w'  in keys:
            movePlayer(app, app.moveSpeed)
        if 's' in keys:
            movePlayer(app, -app.moveSpeed)

def onMousePress(app, mouseX, mouseY):
    if app.page == "homepage":
        if 220 <= mouseX <= 480 and 725 <= mouseY <= 775:
            app.page = "mainpage"

def toggleMusic(app):
    if app.musicOn:
        app.music.pause()
        app.musicOn = False
    else:
        app.music.play(loop=True)
        app.musicOn = True

def movePlayer(app, distance):
    newX = app.playerX + math.cos(app.playerAngle) * distance
    newY = app.playerY + math.sin(app.playerAngle) * distance
    if app.worldMap[int(newY)][int(newX)] == 0:
        app.playerX = newX
        app.playerY = newY

def castRay(app, angle):
    x, y = app.playerX, app.playerY
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    
    while True:
        x += 0.1 * cos_a
        y += 0.1 * sin_a
        
        map_x, map_y = int(x), int(y)
        
        if app.worldMap[map_y][map_x] == 1:
            distance = math.sqrt((x - app.playerX)**2 + (y - app.playerY)**2)
            return distance

def redrawAll(app):
    if app.page == "homepage":
        drawLabel("Beggar Life", 500, 100, size=64)
        drawLabel("Unlock your true money grabbing potential", 500, 175, size=32)
        
        drawRect(220, 725, 260, 50, fill=None, border="black", borderWidth=5)
        drawLabel("Start Game", 350, 750, size=16)
        
        drawLabel("Credits", 600, 750, size=16)
        drawLabel("Credits#2", 900, 750, size=16)
        
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20)
    
    elif app.page == "mainpage":
        # Draw sky
        drawRect(0, 0, app.width, app.height/2, fill='skyBlue')
        # Draw ground
        drawRect(0, app.height/2, app.width, app.height/2, fill='green')
        
        # Cast rays and draw walls
        for i in range(app.rayCount):
            rayAngle = app.playerAngle - app.fov/2 + (i / app.rayCount) * app.fov
            distance = castRay(app, rayAngle)
            
            # Calculate wall height
            wallHeight = min(app.height, app.height / (distance + 0.0001))
            
            # Draw wall slice
            x = i * (app.width / app.rayCount)
            color = rgb(255 - min(255, int(distance * 20)), 0, 0)
            drawLine(x, app.height/2 - wallHeight/2, x, app.height/2 + wallHeight/2, fill=color)
        
        drawLabel("Use arrow keys to move", 500, 50, size=20)
        drawLabel(f"Player Position: ({app.playerX:.2f}, {app.playerY:.2f})", 500, 100, size=20)
        drawLabel(f"Player Angle: {math.degrees(app.playerAngle):.2f}", 500, 150, size=20)
        
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20)

def main():
    runApp()

main()