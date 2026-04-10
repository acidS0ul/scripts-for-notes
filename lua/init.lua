#!/usr/bin/env lua
-- Main entry point for the Lua markdown links manager
-- Lua 5.1 compatible

package.path = package.path .. ';' .. arg[0]:match('(.*/)') .. '?.lua'

local cli = require('cli')
return cli.main(arg)