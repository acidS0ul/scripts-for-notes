-- File utilities for finding and reading files
-- Lua 5.1 compatible

local M = {}

function M.find_files(extension, root)
    root = root or '.'
    local files = {}
    
    local function scan(dir)
        local handle = io.popen('dir "' .. dir .. '" /B /S 2>nul')
        if not handle then return end
        
        for line in handle:lines() do
            local ext = line:match("%.(%w+)$")
            if ext and ext:gsub("%.", "") == extension:gsub("%.", "") then
                table.insert(files, line)
            end
        end
        handle:close()
    end
    
    scan(root)
    return files
end

function M.read_lines(filename)
    local lines = {}
    local file = io.open(filename, 'r')
    if not file then return nil end
    
    for line in file:lines() do
        table.insert(lines, line)
    end
    file:close()
    return lines
end

function M.write_lines(filename, lines)
    local file = io.open(filename, 'w')
    if not file then return false end
    
    for _, line in ipairs(lines) do
        file:write(line .. '\n')
    end
    file:close()
    return true
end

function M.exists(path)
    local handle = io.popen('if exist "' .. path .. '" echo exists')
    if not handle then return false end
    local result = handle:read('*a')
    handle:close()
    return result:match('exists') ~= nil
end

return M