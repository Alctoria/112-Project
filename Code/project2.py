from cmu_graphics import *
import math
import random

class Page:
    def __init__(self, x, y, image_url):
        self.x = x
        self.y = y
        self.image_url = image_url
        self.is_collected = False
    
    def is_near_player(self, player_x, player_y, threshold=0.5):
        distance = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
        return distance <= threshold
    
    def has_line_of_sight(self, app):
        dx = self.x - app.playerX
        dy = self.y - app.playerY
        
        # Calculate distance
        distance = math.sqrt(dx**2 + dy**2)
        
        # Calculate angle to page
        page_angle = math.atan2(dy, dx)
        
        # Cast a ray to check if there are walls between player and page
        x, y = app.playerX, app.playerY
        step_x = 0.1 * math.cos(page_angle)
        step_y = 0.1 * math.sin(page_angle)
        
        for _ in range(int(distance / 0.1)):
            x += step_x
            y += step_y
            if getWallAt(app, x, y) == 1:
                return False
            if math.sqrt((x - self.x)**2 + (y - self.y)**2) <= 0.1:
                return True
        
        return True
    
    def draw(self, app):
        if not self.is_collected:
            # Calculate screen position relative to player
            dx = self.x - app.playerX
            dy = self.y - app.playerY
            
            # Calculate angle and distance
            angle = math.atan2(dy, dx)
            distance = math.sqrt(dx**2 + dy**2)
            
            # Check if page is in player's field of view
            relative_angle = angle - app.playerAngle
            if abs(relative_angle) < app.fov/2:
                if self.has_line_of_sight(app):
                    # Calculate page's screen position
                    page_screen_x = app.width/2 + math.tan(relative_angle) * app.width/2
                    page_height = min(app.height, app.height / (distance + 0.0001))
                    page_width = page_height / 2  # Maintain aspect ratio
                    
                    # Draw page image
                    drawImage(self.image_url, 
                              page_screen_x - page_width/2, 
                              app.height/2 - page_height/2, 
                              width=page_width, 
                              height=page_height)

class Hazard:
    def __init__(self, x, y, hazard_type):
        self.x = x
        self.y = y
        self.type = hazard_type
        self.duration = 0  # For temporary effects
        self.active = True
        
        # Specific hazard characteristics
        self.severity = random.uniform(0.5, 1.5)
        
        # Visual representation
        self.color_map = {
            'poison': 'green',
            'trap': 'red',
            'darkness': 'purple',
            'slowzone': 'blue'
        }
        
        # Effect duration
        self.effect_duration_map = {
            'poison': 50,
            'trap': 30,
            'darkness': 40,
            'slowzone': 60
        }
    
    def apply_effect(self, app):
        if not self.active:
            return
        
        # Different effects based on hazard type
        if self.type == 'poison':
            app.playerHealth -= 5 * self.severity
        elif self.type == 'trap':
            app.moveSpeed *= (1 - 0.3 * self.severity)
        elif self.type == 'darkness':
            app.flashlightRadius *= (1 - 0.2 * self.severity)
        elif self.type == 'slowzone':
            app.moveSpeed *= (1 - 0.15 * self.severity)
        
        self.duration += 1
        
        # Check if effect should expire
        if self.duration > self.effect_duration_map[self.type]:
            self.active = False
            
            # Reset effects
            if self.type == 'trap':
                app.moveSpeed = app.default_move_speed
            elif self.type == 'darkness':
                app.flashlightRadius = app.default_flashlight_radius

class DynamicLightSystem:
    def __init__(self):
        self.battery_life = 100.0
        self.max_battery = 100.0
        self.battery_drain_rate = 0.3
        self.battery_recharge_rate = 0.1
        
        # Different battery states
        self.battery_states = {
            'full': (0, 100),
            'medium': (30, 70),
            'low': (10, 30),
            'critical': (0, 10)
        }
        
        # Flashlight characteristics
        self.flashlight_modes = {
            'standard': {'radius_multiplier': 1.0, 'drain_multiplier': 1.0},
            'focused': {'radius_multiplier': 0.7, 'drain_multiplier': 0.5},
            'wide': {'radius_multiplier': 1.5, 'drain_multiplier': 1.5}
        }
        
        self.current_mode = 'standard'
    
    def update_battery(self, app):
        if app.flashlightOn:
            mode = self.flashlight_modes[self.current_mode]
            self.battery_life -= self.battery_drain_rate * mode['drain_multiplier']
        else:
            # Slow recharge when not in use
            self.battery_life = min(self.max_battery, 
                                    self.battery_life + self.battery_recharge_rate)
        
        # Check battery states
        self.battery_life = max(0, min(self.battery_life, self.max_battery))
        
        # Disable flashlight if battery is critical
        if self.battery_life <= 0:
            app.flashlightOn = False
    
    def cycle_flashlight_mode(self):
        modes = list(self.flashlight_modes.keys())
        current_index = modes.index(self.current_mode)
        self.current_mode = modes[(current_index + 1) % len(modes)]

def onAppStart(app):

    app.page = "homepage"
    app.width = 1000
    app.height = 1000
    
    app.music = {
        "homepage": Sound("https://vgmsite.com/soundtracks/new-super-luigi-u-2019/ztszdhxgsu/01.%20Title%20Theme.mp3"),
        "mainpage": Sound("https://s3.amazonaws.com/cmu-cs-academy.lib.prod/sounds/Drum1.mp3"),
        "creditspage": Sound("https://s3.amazonaws.com/cmu-cs-academy.lib.prod/sounds/Drum1.mp3"),
        "howtopage": Sound("https://s3.amazonaws.com/cmu-cs-academy.lib.prod/sounds/Drum1.mp3")
    }

    app.url = {
        "Page1" : 'Code/images/IntroPic.jpg',
        "Monster" : 'Code/images/Kozbie.jpg'
    }

    app.musicOn = True
    app.music[app.page].play(loop=True)

    # init code. 
    app.chunkSize = 8  
    app.currentChunk = (0, 0)  
    app.chunks = {}  
    app.chunks[(0, 0)] = generateInitialChunk()  
    
    #player init position/angle
    app.playerX = 1.5
    app.playerY = 1.5
    app.playerAngle = 0
    app.fov = math.pi / 3
    app.rayCount = 250
    app.moveSpeed = 0.1
    app.rotateSpeed = 0.1

    #border radius settings

    app.borderCircleRadius = 20
    app.circlesPerSide = (app.width // (app.borderCircleRadius * 2)) + 2

    # Monster initialization
    app.monsterX = 6.5  # Start monster away from player
    app.monsterY = 6.5
    app.monsterSpeed = 0.003  # Adjust this to change difficulty
    app.gameOver = False
    app.gameOverOpacity = 0
    
    # Add step counter for monster updates
    app.stepsPerSecond = 300

    # Page-related initialization
    app.pages = []  # Will store all page objects
    app.pages_collected = 0
    app.max_pages = 8  # Total pages to collect before game ends

    # Enhanced lighting system
    app.lightSystem = DynamicLightSystem()
    app.flashlightOn = False
    app.default_move_speed = 0.1
    app.default_flashlight_radius = 200
    
    # Expanded hazard system
    app.hazards = []
    app.max_hazards = 5
    app.hazard_generation_cooldown = 0
    
    # Player health and status
    app.playerHealth = 100
    app.playerMaxHealth = 100
    app.healthRegenRate = 0.1
    
    # Mouse look settings
    app.mouseSensitivity = 0.002
    app.lastMouseX = app.width // 2
    app.lastMouseY = app.height // 2


def updateMonsterSpeed(app):
    base_speed = 0.001
    speed_increment = 0.0005
    
    # monster speed
    app.monsterSpeed = base_speed + (app.pages_collected * speed_increment)

def generatePagesInChunk(chunk_x, chunk_y, image_url, total_pages, max_pages):

    if total_pages >= max_pages:
        return []
    
    pages = []
    
    # Very low probability of generating a page
    # This can be adjusted: lower number = fewer pages
    if random.random() < 0.5 and total_pages < max_pages:
        # Find a random empty spot in the chunk
        while True:
            local_x = random.randint(0, 7)
            local_y = random.randint(0, 6)
            
            # World coordinates of the page
            world_x = chunk_x * 8 + local_x + 0.5
            world_y = chunk_y * 7 + local_y + 0.5
            
            # Create and add page
            page = Page(world_x, world_y, image_url)
            pages.append(page)
            break
    
    return pages

def generateInitialChunk():
    return [
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,1,0,0,1,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ]

def generateNewChunk():
    # Generate a new chunk without border walls
    chunk = [[0 for _ in range(8)] for _ in range(7)]
    
    # REDUCE WALL GENERATION PROBABILITY
    # MAKE POSSIBLE CHANGES HERE FOR MORE COMPLEXITY BY CREATING A HIGHER CHANCE OF WALL WITH LEVEL DIFFICULTY
    for y in range(7):
        for x in range(8):
            # WALL PROBABILITY 0.15
            if random.random() < 0.15 and (x, y) != (1, 1):  
                chunk[y][x] = 1
    
    # Ensure the chunk has open space
    for y in range(7):
        hasPath = False
        for x in range(8):
            if chunk[y][x] == 0:
                hasPath = True
                break
        if not hasPath:
            # Create at least one path if none exists
            x = random.randint(0, 7)
            chunk[y][x] = 0
    
    return chunk


def getChunkCoordinates(app, x, y):
    chunkX = int(x // app.chunkSize)
    chunkY = int(y // app.chunkSize)
    return (chunkX, chunkY)

def getLocalCoordinates(app, x, y):

    # Ensure coordinates wrap within chunk boundaries
    localX = int(x % app.chunkSize)
    localY = int(y % app.chunkSize)

    # Prevent accessing out of bounds indices
    localX = min(localX, 7)  # 8 wide (0-7)
    localY = min(localY, 6)  # 7 tall (0-6)
    
    return (localX, localY)

def checkAndGenerateChunks(app, x, y):
    currentChunk = getChunkCoordinates(app, x, y)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            neighborChunk = (currentChunk[0] + dx, currentChunk[1] + dy)
            if neighborChunk not in app.chunks:
                # Generate new chunk
                app.chunks[neighborChunk] = generateNewChunk()
                
                # Uncollected pages
                uncollected_pages = [page for page in app.pages if not page.is_collected]
                
                # If we already have 4 uncollected pages, skip page generation
                if len(uncollected_pages) >= 4:
                    continue
                
                # Generate pages for this chunk
                new_pages = generatePagesInChunk(
                    neighborChunk[0], 
                    neighborChunk[1], 
                    app.url["Page1"],  # Using Kozbie image as placeholder
                    len([page for page in app.pages if not page.is_collected]),  # Current uncollected page count
                    4   # Max 4 pages at a time
                )
                app.pages.extend(new_pages)

def getWallAt(app, x, y):
    chunkCoords = getChunkCoordinates(app, x, y)
    if chunkCoords not in app.chunks:
        return 1  # Return wall if chunk doesn't exist
    
    try:
        localX, localY = getLocalCoordinates(app, x, y)
        return app.chunks[chunkCoords][localY][localX]
    except IndexError:
        # If we somehow still get an index error, return a wall
        return 1

def onKeyPress(app, key):
    if key == 'm':
        toggleMusic(app)
    elif key == 'r' and app.gameOver:
        # Reset game
        app.playerX = 1.5
        app.playerY = 1.5
        app.monsterX = 6.5
        app.monsterY = 6.5
        app.gameOver = False
        app.chunks = {}
        app.chunks[(0, 0)] = generateInitialChunk()

        # Reset page collection
        app.pages = []
        app.pages_collected = 0

def onKeyHold(app, keys):
    if app.page == "mainpage":
        if ('a' in keys or 'left' in keys):
            app.playerAngle -= app.rotateSpeed
        if ('d' in keys or 'right' in keys):
            app.playerAngle += app.rotateSpeed
        if ('w' in keys or 'up' in keys):
            movePlayer(app, app.moveSpeed)
        if ('s' in keys or 'down' in keys):
            movePlayer(app, -app.moveSpeed)

def onMousePress(app, mouseX, mouseY):
    if app.page == "homepage":
        if 180 <= mouseX <= 320 and 725 <= mouseY <= 775:
            app.music[app.page].pause()
            app.page = "mainpage"
            if app.musicOn:
                app.music[app.page].play(loop=True)
        if 430 <= mouseX <= 570 and 725 <= mouseY <= 775:
            app.music[app.page].pause()
            app.page = "howtopage"
            if app.musicOn:
                app.music[app.page].play(loop=True)
        if 680 <= mouseX <= 820 and 725 <= mouseY <= 775:
            app.music[app.page].pause()
            app.page = "creditspage"
            if app.musicOn:
                app.music[app.page].play(loop=True)
    
    if (app.page != "homepage" and app.page != "mainpage"):
        if 825 <= mouseX <= 975 and 85 <= mouseY <= 135:
            app.music[app.page].pause()
            app.page = "homepage"
            if app.musicOn:
                app.music[app.page].play(loop=True)
    
    if (app.gameOver):
        if 500 <= mouseX <= 840 and 575 <= mouseY <= 625:
            app.music[app.page].pause()
            app.page = "homepage"
            if app.musicOn:
                app.music[app.page].play(loop=True)
            app.gameOver = (not app.gameOver)

def toggleMusic(app):
    if app.musicOn:
        app.music[app.page].pause()
        app.musicOn = False
    else:
        app.music[app.page].play(loop=True)
        app.musicOn = True

def movePlayer(app, distance):
    newX = app.playerX + math.cos(app.playerAngle) * distance
    newY = app.playerY + math.sin(app.playerAngle) * distance
    
    # Ensure coordinates stay within valid ranges
    if newX < 0: newX = 0
    if newY < 0: newY = 0
    
    checkAndGenerateChunks(app, newX, newY)
    
    # Only move if the new position is not a 1 (wall)
    try:
        if getWallAt(app, newX, newY) == 0:
            app.playerX = newX
            app.playerY = newY
    except IndexError:
        pass  # SKIP

def castRay(app, angle):
    x, y = app.playerX, app.playerY
    sin_a = math.sin(angle)
    cos_a = math.cos(angle)
    try:
        while True:
            x += 0.1 * cos_a
            y += 0.1 * sin_a
            
            if x < 0 or y < 0:
                return math.sqrt((x - app.playerX)**2 + (y - app.playerY)**2)
            
            if getWallAt(app, x, y) == 1:
                wall_check_offsets = [
                    (0, 0),
                    (0.05, 0),
                    (-0.05, 0),
                    (0, 0.05),
                    (0, -0.05)
                ]
                
                for dx, dy in wall_check_offsets:
                    if getWallAt(app, x + dx, y + dy) == 1:
                        distance = math.sqrt((x - app.playerX)**2 + (y - app.playerY)**2)
                        return distance
            
    except IndexError:
        return math.sqrt((x - app.playerX)**2 + (y - app.playerY)**2)


def updateMonster(app):
    if app.gameOver:
        return
        
    # Calculate direction to player
    dx = app.playerX - app.monsterX
    dy = app.playerY - app.monsterY
    
    # Calculate distance to player
    distance = math.sqrt(dx**2 + dy**2)
    
    # Check for game over condition
    if distance < 0.2:
        app.gameOver = True
        return
        
    # Normalize direction
    if distance > 0:
        dx /= distance
        dy /= distance
    
    # Calculate new position
    app.monsterX = app.monsterX + dx * app.monsterSpeed
    app.monsterY = app.monsterY + dy * app.monsterSpeed
    
    # This function makes it where the monster can walk through walls or not
    #if getWallAt(app, newX, newY) == 0:
       #app.monsterX = newX
       #app.monsterY = newY

def onStep(app):
    if app.page == "mainpage" and not app.gameOver:
        updateMonsterSpeed(app)
        updateMonster(app)
        
        # Check if player can collect pages
        for page in app.pages:
            if not page.is_collected and page.is_near_player(app.playerX, app.playerY):
                page.is_collected = True
                app.pages_collected += 1
                
                # Check for game win condition
                if app.pages_collected >= app.max_pages:
                    app.gameOver = True
def redrawAll(app):
    
    if app.page == "creditspage":
        drawLabel("This is the creditspage", 200, 200)
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20)
        drawRect(825, 25, 150, 50, fill=None, border="black", borderWidth=5)
        drawLabel('To Homepage', 900, 110, size=20)
        drawRect(825, 85, 150, 50, fill=None, border="black", borderWidth=5)

    elif app.page == "howtopage":
        drawLabel("How to Play 112 BackRooms!", 200, 200)
        drawLabel("There are scary monsters (cough) chasing you in this game..", 200, 300)
        drawLabel("The goal in this game is to run away, while obtaining 8 pages that are randomly distributed throughout the map!", 200, 400)
        drawLabel("Keep in mind that the map is auto generated as you stray away from spawn.", 200, 500)
        drawLabel("You can only see the monster when it is faced in front of you!", 200, 600)
        drawLabel("This means that if you don't see the monster, it might be behind you!", 200, 700)
        drawLabel("There will be a scary sound whenever the monster is close to you!", 200, 800)
        drawImage(app.url["Monster"], 800, 500)
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20)
        drawRect(825, 25, 150, 50, fill=None, border="black", borderWidth=5)
        drawLabel('To Homepage', 900, 110, size=20)
        drawRect(825, 85, 150, 50, fill=None, border="black", borderWidth=5)
        
    elif app.page == "homepage":
        drawLabel("112 BackRooms", 500, 100, size=64)
        drawLabel("Collect 8 pages as you run away from scary monsters!", 500, 175, size=32)
        
        drawRect(180, 725, 140, 50, fill=None, border="black", borderWidth=5)
        drawLabel("Start Game", 250, 750, size=16)
        
        drawRect(430, 725, 140, 50, fill=None, border="black", borderWidth=5)
        drawLabel("How to Play", 500, 750, size=16)

        drawRect(680, 725, 140, 50, fill=None, border="black", borderWidth=5)
        drawLabel("Credits", 750, 750, size=16)
        
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20)
        drawRect(825, 25, 150, 50, fill=None, border="black", borderWidth=5)
    
    elif app.page == "mainpage":
        # Draw sky
        drawRect(0, 0, app.width, app.height/2, fill='white')
        # Draw ground
        drawRect(0, app.height/2, app.width, app.height/2, fill='yellow')
        
        # Cast rays and draw walls
        for i in range(app.rayCount):
            rayAngle = app.playerAngle - app.fov/2 + (i / app.rayCount) * app.fov
            distance = castRay(app, rayAngle)
            
            # Calculate wall height
            wallHeight = min(app.height, app.height / (distance + 0.0001))
            
            # Draw wall slice
            x = i * (app.width / app.rayCount)
            drawLine(x, app.height/2 - wallHeight/2, x, app.height/2 + wallHeight/2, fill="black")
        
        # Draw monster (basic representation)
        monsterAngle = math.atan2(app.monsterY - app.playerY, app.monsterX - app.playerX)
        monsterRelativeAngle = monsterAngle - app.playerAngle
        monsterDistance = math.sqrt((app.monsterX - app.playerX)**2 + (app.monsterY - app.playerY)**2)
        
        # Only draw monster if it's in front of the player
        if abs(monsterRelativeAngle) < app.fov/2:
            # Calculate monster's screen position
            monsterScreenX = app.width/2 + math.tan(monsterRelativeAngle) * app.width/2
            monsterHeight = min(app.height, app.height / (monsterDistance + 0.0001))
            monsterWidth = monsterHeight / 2  # Maintain aspect ratio
            
            # Draw monster using drawImage with the URL directly
            drawImage(app.url["Monster"], monsterScreenX - monsterWidth/2, app.height/2 - monsterHeight/2, width=monsterWidth, height=monsterHeight)
        
        # Draw UI elements
        drawLabel("Use arrow keys to move", 500, 50, size=20, fill='red')
        drawLabel(f"Player Position: ({app.playerX:.2f}, {app.playerY:.2f})", 500, 100, size=20, fill='red')
        drawLabel(f"Distance to Monster: {monsterDistance:.2f}", 500, 150, size=20, fill='red')
        
        musicStatus = "Music: ON" if app.musicOn else "Music: OFF"
        drawLabel(musicStatus, 900, 50, size=20, fill='red')
        drawRect(825, 25, 150, 50, fill=None, border="red", borderWidth=5)

        for page in app.pages:
            page.draw(app)
        
        # Display pages collected
        drawLabel(f"Pages Collected: {app.pages_collected}/{app.max_pages}", 
                  500, 200, size=20, fill='red')

        if app.gameOver:
            drawRect(0, 0, app.width, app.height, fill='black', opacity=80)   
            # Draw game over text
            drawLabel("GAME OVER", app.width/2, app.height/2, size=64, fill='red', bold=True)
            drawLabel("Press 'R' to restart", app.width/3, app.height/2 + 100, size=32, fill='red')
            drawLabel("Go Back to Homepage", app.width * 2/3, app.height/2 + 100, size = 32, fill = 'red')
            drawRect(190,575,285,50,fill = None, border = 'red')
            drawRect(500,575,340,50,fill = None, border = 'red')


    
    if app.page != 'mainpage': #not mainpage as mainpage is the gameplay page!
        #draw borders, all four sides
        for i in range(app.circlesPerSide):
            x = i * (app.borderCircleRadius * 2)
            drawArc(x, 0, app.borderCircleRadius * 2, app.borderCircleRadius * 2, 180, 180, fill='black')
        for i in range(app.circlesPerSide):
            x = i * (app.borderCircleRadius * 2)
            drawArc(x, app.height, app.borderCircleRadius * 2, app.borderCircleRadius * 2, 0, 180, fill='black')
        for i in range(app.circlesPerSide):
            y = i * (app.borderCircleRadius* 2)
            drawArc(0, y, app.borderCircleRadius * 2, app.borderCircleRadius * 2, 180, 360, fill='black')
        for i in range(app.circlesPerSide):
            y = i * (app.borderCircleRadius * 2)
            drawArc(app.width, y, app.borderCircleRadius * 2, app.borderCircleRadius * 2, 90, 270, fill='black')

def main():
    runApp()

main()