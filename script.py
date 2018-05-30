import mdl
from display import *
from matrix import *
from draw import *

basename = ""
num_frames = 0
knobs = []
"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)

  Should set num_frames and basename if the frames
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  ==================== """


def first_pass(commands):
    frameFound = False
    varyFound = False
    fileFound = False
    global num_frames
    global basename
    for command in commands:
        c = command['op']
        if c == 'frames':
            frameFound = True
            num_frames = command["args"][0]
            #if not basenameFound(filename):
            #basename="anim"
            #print "Default filename: 'anim'"
        elif c == 'basename':
            baseFound = True
            basename = command["args"]
        elif c == 'vary':
            varyFound = True
    if varyFound and not frameFound:
        exit()
    if frameFound and not fileFound:
        basename = "anim"
        print "Default filename: 'anim'"
    #print commands


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a separate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropriate value.
  ===================="""

#symbol table: {'spinny': ['knob', 0], 'bigenator': ['knob', 0]}
#commands: {'knob': 'bigenator', 'args': [50.0, 99.0, 1.0, 0.0], 'op': 'vary'}]


def second_pass(commands, num_frames):
    global knobs
    for i in range(int(num_frames)):
        knobs.append({})
    for command in commands:
        if command["op"] == "vary":
            knobname = command["knob"]
            args = command["args"]
            startFrame = args[0]
            endFrame = args[1]
            start = args[2]
            end = args[3]
            print str(start) + " " + str(end) + " " + str(num_frames)
            toVary = (end - start + 0.0) / (endFrame - startFrame)
            print str(toVary)
            if startFrame > num_frames - 1 or endFrame > num_frames - 1 or endFrame < startFrame or startFrame < 0 or endFrame < 0:
                print "Invalid range or frame"
                exit()
            j = startFrame
            while j < endFrame + 1:
                knobs[int(j)][knobname] = start + (
                    (j - startFrame) * toVary)  #dict
                j += 1


def run(filename):
    """
    This function runs an mdl script
    """
    view = [0, 0, 1]
    ambient = [50, 50, 50]
    light = [[0.5, 0.75, 1], [0, 255, 255]]
    areflect = [0.1, 0.1, 0.1]
    dreflect = [0.5, 0.5, 0.5]
    sreflect = [0.5, 0.5, 0.5]

    color = [0, 0, 0]
    tmp = new_matrix()
    ident(tmp)
    stack = [[x[:] for x in tmp]]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 20
    consts = ''
    coords = []
    coords1 = []
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return
    first_pass(commands)
    second_pass(commands, num_frames)
    for frame in range(int(num_frames)):
        for knob in knobs[frame]:  #knob is the knobname
            if knobs[frame][knob] is None:
                symbols[knob][1] = 1
            else:
                symbols[knob][1] = knobs[frame][knob]
        for command in commands:
            c = command['op']
            args = command['args']
            if "knob" in command and c in [
                    "move", "scale", "rotate"
            ] and (not command["knob"] == None) and (not args == None):
                args = command['args'][:]
                knob = command["knob"]
                for i in range(len(args)):
                    if not isinstance(args[i], basestring):
                        args[i] = args[i] * symbols[knob][1]
            if c == 'box':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[-1], str):
                    coords = args[-1]
                add_box(tmp, args[0], args[1], args[2], args[3], args[4],
                        args[5])
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light,
                              areflect, dreflect, sreflect)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp, args[0], args[1], args[2], args[3], step_3d)
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light,
                              areflect, dreflect, sreflect)
                tmp = []
            elif c == 'torus':
                add_torus(tmp, args[0], args[1], args[2], args[3], args[4],
                          step_3d)
                matrix_mult(stack[-1], tmp)
                draw_polygons(tmp, screen, zbuffer, view, ambient, light,
                              areflect, dreflect, sreflect)
                tmp = []
            elif c == 'line':
                if isinstance(args[0], str):
                    consts = args[0]
                    args = args[1:]
                if isinstance(args[3], str):
                    coords = args[3]
                    args = args[:3] + args[4:]
                if isinstance(args[-1], str):
                    coords1 = args[-1]
                add_edge(tmp, args[0], args[1], args[2], args[3], args[4],
                         args[5])
                matrix_mult(stack[-1], tmp)
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi / 180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]])
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        if num_frames > 1:
            save_extension(screen, ("./anim/" + basename +
                                    ("%03d" % int(frame)) + ".png"))
        tmp = new_matrix()
        ident(tmp)
        stack = [[x[:] for x in tmp]]
        screen = new_screen()
        zbuffer = new_zbuffer()
        tmp = []
        step_3d = 20
    if num_frames > 1:
        make_animation(basename)


#run("simple_anim.mdl")
