#!/usr/bin/env python
# a quick script to test things
# example: >>> reload(run) ; run.run()
# from script import run; reload(run); run.run()


from pyx import *


def run():
    gridsize = [[-2.5,3],[-1,4]]

    # unit.set(wscale=1)
    unit.set(defaultunit="inch")

    # help(graph.axis.linear)
    # parter = graph.axis.parter.linear([.2,.4,.6])
    texter = graph.axis.texter.mixed(graph.axis.tick.rational((1, 1)))

    g = graph.graphxy(width=4, height=3,
                  x=graph.axis.linear(min=gridsize[0][0], 
                                      max=gridsize[0][1],
                                      title='X [inch]'),
                  y=graph.axis.linear(min=gridsize[1][0], 
                                      max=gridsize[1][1],
                                      title='Y [inch]'))
    g.plot(graph.data.points(zip(range(10), range(10)), x=1, y=2))
    g.plot(graph.data.points(zip(range(10), range(1,10+1)), x=1, y=2),
            [graph.style.line([style.linewidth.Thin, 
                               color.rgb.blue,
                                style.linestyle.solid]),
             graph.style.symbol(graph.style.symbol.circle, size=0.1,
                           symbolattrs=[deco.filled([color.rgb.green]),
                                        deco.stroked([color.rgb.red])])])


    g.writeEPSfile("fig1.eps")
    # c = canvas.canvas()
    # c.stroke(path.line(0, 0, 3, 0))
    # c.stroke(path.rect(0, 1, 1, 1))
    # c.fill(path.circle(2.5, 1.5, 0.5))

    # c.writeEPSfile("fig1.eps")

from  lib.tool import IndexDict, origin
def test():
  x = origin()
  print x
  print x.allkeys()
  for i in [1, 'x','X']:
    print i,x[i]
  
  print x.x, x.y, x.z



  # x = IndexDict()
  #   print x
  #   print x[0]
  #   
  #   x[0] = 0.1
  #   print x
  #   x['y'] = 0.2
  #   x['Z'] = 0.3
  #   # 
  #   print x
  


if __name__ == '__main__':
  test()
  
