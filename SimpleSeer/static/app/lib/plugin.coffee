module.exports = (cls, plugins) =>
  if cls._plugins?
    _plugins = cls._plugins
  else
    _plugins = cls._plugins = {}
    cls.getPlugin = (name) => _plugins[name]
    cls.getPlugin = (name) ->
      _plugins[name]
    cls.prototype.getPlugin = (name) ->
      unless _plugins.name?
        return undefined
      Plugin = _plugins[name]
      new Plugin(this)
  for name, plugin of plugins
    _plugins[name] = plugin