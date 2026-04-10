#!/usr/bin/env lua
-- CLI for managing markdown links and backlinks
-- Lua 5.1 compatible

local M = {}

local function parse_args(args)
    local opts = {
        wiki = false,
        back = false,
        path = nil,
        dir = nil,
        verbose = false
    }
    
    local i = 1
    while i <= #args do
        local arg = args[i]
        if arg == '-h' or arg == '--help' then
            print('-h, --help     - this message')
            print('-w, --wiki     - replace wiki links')
            print('-v             - verbose')
            print('-b, --back     - update backlinks')
            print('-p, --path     - root path for media')
            print('-d, --dir      - working directory')
            os.exit(0)
        elseif arg == '-v' or arg == '--verbose' then
            opts.verbose = true
        elseif arg == '-w' or arg == '--wiki' then
            opts.wiki = true
        elseif arg == '-b' or arg == '--back' then
            opts.back = true
        elseif arg == '-p' or arg == '--path' then
            i = i + 1
            opts.path = args[i]
        elseif arg == '-d' or arg == '--dir' then
            i = i + 1
            opts.dir = args[i]
        end
        i = i + 1
    end
    
    return opts
end

local function find_files(extension, root)
    root = root or '.'
    local files = {}
    
    local handle = io.popen('dir "' .. root .. '" /B /S 2>nul')
    if not handle then return files end
    
    for line in handle:lines() do
        if line:ends_with(extension) then
            table.insert(files, line)
        end
    end
    handle:close()
    
    return files
end

function M.main(args)
    args = args or arg
    local opts = parse_args(args)
    
    if opts.dir then
        local ok, err = os.execute('cd "' .. opts.dir .. '"')
        if not ok then
            print('Error: dir ' .. opts.dir .. ' not found')
            return 1
        end
    end
    
    local file_extension = '.md'
    local files = find_files(file_extension)
    
    local link_processor = require('link_processor')
    local backlinks_mod = require('backlinks')
    
    if opts.path then
        for _, file in ipairs(files) do
            local file_handle = io.open(file, 'r')
            if file_handle then
                local content = file_handle:read('*all')
                file_handle:close()
                
                local new_content = link_processor.fix_media_path(content, opts.path)
                
                file_handle = io.open(file, 'w')
                if file_handle then
                    file_handle:write(new_content)
                    file_handle:close()
                end
            end
        end
    end
    
    if opts.wiki then
        for _, file in ipairs(files) do
            if opts.verbose then
                print(file)
            end
            
            local file_handle = io.open(file, 'r')
            if file_handle then
                local content = file_handle:read('*all')
                file_handle:close()
                
                content = link_processor.wiki_to_markdown(content)
                content = link_processor.media_wiki_to_markdown(content)
                
                file_handle = io.open(file, 'w')
                if file_handle then
                    file_handle:write(content)
                    file_handle:close()
                end
            end
        end
    end
    
    if opts.back then
        local database = backlinks_mod.create_links_database(files)
        local new_backlinks = backlinks_mod.find_new_backlinks(database, opts.verbose)
        backlinks_mod.add_new_backlinks(new_backlinks)
    end
    
    return 0
end

return M