# pyteleor

A python module that supports teleo-reactive agents.

``` G : (c_1, c_2, ... ) -> (a1, a2, ... ) ```

Example TR program `robot.pytr` using the ```pytr``` interpreted language.

```
grid_size == None -> find_grid_size()
-> speaker(speak(grid_size))

find_grid_size():
    orientation == north -> motor(turn(right))
    orientation == west -> motor(turn(left))

    orientation == east, x >= y -> motor(move)
    orientation == east, x < y -> motor(turn(right))
    
    orientation == south, y >= x -> motor(move)
    orientation == south, y < x -> motor(turn(left))
```

A serialised implemenation is currently in the works, concurrent rule evaluation is in the works.

Currently in development and very unstable.
