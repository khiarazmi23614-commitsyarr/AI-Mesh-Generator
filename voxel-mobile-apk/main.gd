extends Node3D
const SIZE=20
var blocks={}
var nodes={}
var player:CharacterBody3D
var cam:Camera3D
var joy:Control
var joy_value=Vector2.ZERO
var yaw=0.0
var pitch=-0.2
var selected=0
var inventory=[32,32,32]
var mats=[]

func _ready():
    _materials(); _world(); _player(); _ui()

func _materials():
    for c in [Color("#63ad4d"),Color("#8b5a35"),Color("#888d94")]:
        var m=StandardMaterial3D.new(); m.albedo_color=c; mats.append(m)

func _world():
    var mesh=BoxMesh.new(); mesh.size=Vector3.ONE
    for x in range(-SIZE/2,SIZE/2):
        for z in range(-SIZE/2,SIZE/2):
            var h=2+int((sin(x*.5)+cos(z*.4))*.5); h=clamp(h,1,4)
            for y in range(h): _add_block(Vector3i(x,y,z),0 if y==h-1 else (1 if y>=h-3 else 2),mesh)
    var sun=DirectionalLight3D.new(); sun.rotation_degrees=Vector3(-55,-30,0); add_child(sun)
    var env=WorldEnvironment.new(); var e=Environment.new(); e.background_mode=Environment.BG_COLOR; e.background_color=Color("#88b8e8"); e.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR; e.ambient_light_energy=.6; env.environment=e; add_child(env)

func _add_block(p:Vector3i,t:int,mesh:BoxMesh):
    blocks[p]=t; var b=StaticBody3D.new(); b.position=Vector3(p)+Vector3.ONE*.5
    var mi=MeshInstance3D.new(); mi.mesh=mesh; mi.material_override=mats[t]; b.add_child(mi)
    var cs=CollisionShape3D.new(); var sh=BoxShape3D.new(); sh.size=Vector3.ONE; cs.shape=sh; b.add_child(cs); add_child(b); nodes[p]=b

func _remove_block(p):
    if not blocks.has(p): return
    blocks.erase(p); nodes[p].queue_free(); nodes.erase(p)

func _player():
    player=CharacterBody3D.new(); player.position=Vector3(0,6,5); add_child(player)
    var cs=CollisionShape3D.new(); var cap=CapsuleShape3D.new(); cap.height=1.7; cap.radius=.32; cs.shape=cap; cs.position.y=.85; player.add_child(cs)
    cam=Camera3D.new(); cam.position=Vector3(0,1.55,0); player.add_child(cam); cam.current=true; _rot()

func _physics_process(d):
    var v=joy_value
    var f=-player.global_transform.basis.z; var r=player.global_transform.basis.x; var mv=r*v.x+f*(-v.y)
    player.velocity.x=mv.x*4.5; player.velocity.z=mv.z*4.5; player.velocity.y += -20*d if not player.is_on_floor() else 0
    if player.is_on_floor(): player.velocity.y=-.5
    player.move_and_slide()
    if player.position.y < -8: player.position=Vector3(0,6,5)

func _rot(): player.rotation.y=yaw; cam.rotation.x=pitch

func _ui():
    var layer=CanvasLayer.new(); add_child(layer)
    var cross=Label.new(); cross.text="+"; cross.add_theme_font_size_override("font_size",32); cross.position=Vector2(635,325); layer.add_child(cross)
    joy=Control.new(); joy.position=Vector2(40,490); joy.size=Vector2(180,180); layer.add_child(joy); joy.gui_input.connect(_joy)
    var base=ColorRect.new(); base.color=Color(0,0,0,.4); base.position=Vector2(10,10); base.size=Vector2(160,160); base.mouse_filter=Control.MOUSE_FILTER_IGNORE; joy.add_child(base)
    var knob=ColorRect.new(); knob.name="Knob"; knob.color=Color(1,1,1,.75); knob.position=Vector2(65,65); knob.size=Vector2(50,50); knob.mouse_filter=Control.MOUSE_FILTER_IGNORE; joy.add_child(knob)
    _button(layer,"⛏",Vector2(1040,480),false); _button(layer,"▣",Vector2(1150,480),true)
    var inv=HBoxContainer.new(); inv.position=Vector2(470,635); inv.add_theme_constant_override("separation",8); layer.add_child(inv)
    for i in 3:
        var b=Button.new(); b.text=str(inventory[i]); b.custom_minimum_size=Vector2(100,60); b.pressed.connect(func(): selected=i); inv.add_child(b)

func _button(layer,text,pos,place):
    var b=Button.new(); b.text=text; b.position=pos; b.size=Vector2(90,90); b.add_theme_font_size_override("font_size",30); b.pressed.connect(func(): _action(place)); layer.add_child(b)

func _action(place):
    var q=PhysicsRayQueryParameters3D.create(cam.global_position,cam.global_position + -cam.global_transform.basis.z*7); q.exclude=[player]
    var h=get_world_3d().direct_space_state.intersect_ray(q)
    if h.is_empty(): return
    var n=h.normal; var p=Vector3i(floor(h.position-n*.01)) if not place else Vector3i(floor(h.position+n*.51))
    if place:
        if inventory[selected]>0 and not blocks.has(p):
            var mesh=BoxMesh.new(); mesh.size=Vector3.ONE; _add_block(p,selected,mesh); inventory[selected]-=1
    else: _remove_block(p)

func _joy(e):
    var center=Vector2(90,90)
    if e is InputEventScreenTouch:
        if e.pressed: _set_joy(e.position-center)
        else: joy_value=Vector2.ZERO; joy.get_node("Knob").position=Vector2(65,65)
    elif e is InputEventScreenDrag: _set_joy(e.position-center)

func _set_joy(v):
    v=v.limit_length(65); joy_value=v/65.0; joy.get_node("Knob").position=Vector2(65,65)+v

func _input(e):
    if e is InputEventScreenDrag and e.position.x>300 and e.position.x<980 and e.position.y<620:
        yaw-=e.relative.x*.006; pitch=clamp(pitch-e.relative.y*.006,-1.3,1.3); _rot()
