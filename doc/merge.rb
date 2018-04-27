def include_tex(code)
  code.gsub /\\input{(.+)}/ do
    include_tex(File.read(Regexp.last_match[1] + ".tex"))
  end
end

File.write('thesis-merged.tex', include_tex(File.read('thesis.tex')))
