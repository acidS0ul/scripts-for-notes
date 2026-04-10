-- Backlinks manager for markdown files
-- Lua 5.1 compatible

local M = {}

function M.find_links(file_path)
    local file = io.open(file_path, 'r')
    if not file then return nil end
    
    local content = file:read('*all')
    file:close()
    
    local lines_before_bk = {}
    local lines_after_bk = {}
    local backlinks_found = false
    
    for line in content:gmatch('[^\n]+') do
        if not backlinks_found then
            table.insert(lines_before_bk, line)
            if line:match('^backlinks:%s*$') then
                backlinks_found = true
            end
        else
            table.insert(lines_after_bk, line)
        end
    end
    
    if not backlinks_found then
        print('In "' .. file_path .. '" not found "backlinks:" string')
        return nil
    end
    
    local links = {}
    for link in table.concat(lines_before_bk, '\n'):gmatch('%[([^%]]+)%]%(([^)]+)%)') do
        table.insert(links, link)
    end
    
    local backlinks = {}
    for line in table.concat(lines_after_bk, '\n') do
        for link in line:gmatch('%[([^%]]+)%]%(([^)]+)%)') do
            table.insert(backlinks, '[' .. link .. '](' .. link .. ')')
        end
    end
    
    return {links, backlinks}
end

function M.format_links(links)
    local result = {}
    for _, link in ipairs(links) do
        local filename = link:match('%((.+)%)')
        if filename then
            table.insert(result, '[' .. filename .. '](' .. filename .. ')')
        end
    end
    return result
end

function M.extract_filename(link)
    return link:match('%((.+)%)') or ''
end

function M.filename_to_markdown_link(file)
    local name = file:gsub('%.md$', ''):gsub('_', ' ')
    return '[' .. name .. '](' .. file .. ')'
end

function M.create_links_database(files)
    local database = {}
    for _, file_path in ipairs(files) do
        local links = M.find_links(file_path)
        if links then
            links[1] = M.format_links(links[1])
            local basename = file_path:match('([^/\\]+)$')
            database[basename] = links
        end
    end
    return database
end

function M.find_new_backlinks(database, verbose)
    local new_backlinks = {}
    
    for key, data in pairs(database) do
        for _, link in ipairs(data[1]) do
            local filename = M.extract_filename(link)
            if not database[filename] then
                goto continue
            end
            
            if not new_backlinks[filename] then
                new_backlinks[filename] = {}
            end
            
            local new_backlink = M.filename_to_markdown_link(key)
            local is_found = false
            
            for _, backlink in ipairs(database[filename][2]) do
                if link:find(backlink, 1, true) then
                    is_found = true
                    break
                end
            end
            
            if not is_found then
                for _, old_bk in ipairs(database[filename][2]) do
                    if new_backlink:find(old_bk, 1, true) then
                        is_found = true
                        break
                    end
                end
            end
            
            if not is_found then
                local found = false
                for _, bk in ipairs(new_backlinks[filename]) do
                    if bk == new_backlink then
                        found = true
                        break
                    end
                end
                if not found then
                    table.insert(new_backlinks[filename], new_backlink)
                    if verbose then
                        print('new backlink ' .. new_backlink .. ' in ' .. filename .. ' from ' .. key)
                    end
                end
            end
            
            ::continue::
        end
    end
    
    return new_backlinks
end

function M.add_new_backlinks(info)
    for file, bks in pairs(info) do
        local lines = {}
        local file_handle = io.open(file, 'r')
        if not file_handle then
            print('Cannot open file: ' .. file)
            goto next_file
        end
        
        for line in file_handle:lines() do
            table.insert(lines, line)
        end
        file_handle:close()
        
        local inserted = false
        for i, line in ipairs(lines) do
            if line:match('^backlinks:%s*$') then
                for _, bk in ipairs(bks) do
                    table.insert(lines, i + 1, '- ' .. bk)
                end
                inserted = true
                break
            end
        end
        
        if not inserted then
            print('In "' .. file .. '" not found "backlinks:" string')
            goto next_file
        end
        
        file_handle = io.open(file, 'w')
        if file_handle then
            for _, line in ipairs(lines) do
                file_handle:write(line .. '\n')
            end
            file_handle:close()
        end
        
        ::next_file::
    end
end

return M