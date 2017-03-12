# denite-make #

*denite-make* is an source for [dein.nvim](https://github.com//Shougo/denite.nvim).
It provdes an interface to GNU Make. Therefore it utilizes the capabilities
of denite.nvim to execute `make` in an asynchronously and display the output
in the denite buffer.

*denite-make* also supports parsing the output of multiprocess builds (e.g.
`make -j 4`). Therefore it uses a script that wraps the make command. This has
the advantage that the relative file paths of compiler messages can be
matched correctly.

It is also possible to modify the shell wrapper for the make command. This
opens the possibility to use shell specific commands or settings as make
prerequisites.

## Install ##

**Note:** *denite-make* requires an existing installation of dein.nvim which can
be found at https://github.com//Shougo/denite.nvim.

For installation just add the following line to your (N)Vim startup file,
depending on the plugin manager you are using.

For vim-plug:
```
    Plug 'JoZie/denite-make'
```

For dein.vim:
```
   call dein#add('JoZie/denite-make')
```

## Usage ##

A Make command in the current directory can be executed by using `make` as
`:Denite` source. This will show the complete output in the denite.nvim buffer.

The *denite-make* source can also be called with three arguments. In denite.nvim
each one is separated by a colon ':'.
Note: Since denite.nvim sources are separated by space it is required that all
spaces in the arguments are escaped.

    1. Make setup (pre-command)
    This argument specifies a command or an series of commands that will run
    just before the make command. An use case would be to load environment
    modules necessary for make. To work correctly the pre-command has to end
    with a valid expression that enables the combination of shell commands
    e.g. && or ||.

    2. Make arguments
    If specified this arguments are passed directly to the make command. An
    example would be a call to `make -j5 install` . For more options see the
    man page or help of make.

    3. Make directory (build directory)
    If provided, this option specifies the directory the make command is
    executed in. If not, the current directory is used.

A call to *denite-make* with all options provided could look like:
    `:DeniteProjectDir make:module\ load\ gcc\ &&:-j5:build`

## Configuration ##


