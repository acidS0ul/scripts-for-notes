-- Link processor for markdown files
-- Lua 5.1 compatible

local M = {}

function M.wiki_to_markdown(content)
    -- Convert [[name]] to [name](name.md)
    return content:gsub('%[%[(.-)%]%]', function(name)
        return string.format('[%s](%s.md)', name, name)
    end)
end

function M.media_wiki_to_markdown(content)
    -- Convert ![[media]] to ![](media)
    return content:gsub('!%[%[(.-)%]%]', function(name)
        return string.format('![%s](%s)', name, name)
    end)
end

function M.fix_media_path(content, root_dir)
    -- Fix media file paths: ![...](filename) -> ![...](root_dir/filename)
    return content:gsub('!%[([^%]]*)%]%(([^)]+)%)', function(desc, filename)
        if filename:match('^http') then
            return string.format('![%s](%s)', desc, filename)
        end
        return string.format('![%s](%s%s)', desc, root_dir, filename)
    end)
end

function M.replace_in_file(file_path, pattern, replacement)
    local file = io.open(file_path, 'r')
    if not file then return false end
    
    local content = file:read('*all')
    file:close()
    
    local new_content = content:gsub(pattern, replacement)
    
    file = io.open(file_path, 'w')
    if not file then return false end
    
    file:write(new_content)
    file:close()
    return true
end

function M.replace_wiki_links_in_file(file_path)
    local content = M.wiki_to_markdown(content)
    local file = io.open(file_path, 'r')
    if not file then return false end
    content = file:read('*all')
    file:close()
    
    content = M.wiki_to_markdown(content)
    content = M.media_wiki_to_markdown(content)
    
    file = io.open(file_path, 'w')
    if not file then return false end
    file:write(content)
    file:close()
    return true
end

return M