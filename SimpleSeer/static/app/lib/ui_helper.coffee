#application = require '../application'

module.exports = class Pallette
  currentScheme: "candy"
  schemes:
    candy:
      red: {default: 2, shades: ["#C53B3B", "#F80000", "#BA0000", "#F84A4A", "#780000"]}
      orange: {default: 2, shades: ["#FF8859", "#7F2906", "#FF510D", "#7F442C", "#CC420A"]}
      yellow: {default: 2, shades: ["#FFB04C", "#7F4800", "#FF8F00", "#7F5826", "#CC7300"]}
      green: {default: 2, shades: ["#6D902B", "#7FC200", "#507A00", "#93C23A", "#2C4300"]}
      blue: {default: 2, shades: [ "#012340", "#183E4C", "#3D736D", "#8EBF9F", "#E9F2C9"]}
      purple: {default: 2, shades: ["#423842", "#753F72", "#291628", "#756274", "#C268BD"]}


  getColor: (name) =>
    #getColor('red')
    return @.schemes[@currentScheme][name].shades[@.schemes[@currentScheme][name].default]
  getShades: (name) =>
    #getShades('red')
    return @.schemes[@currentScheme][name].shades
  setScheme: (scheme) =>
    if scheme in @schemes
      @.currentScheme = scheme
    else
      console.error "invalid scheme"
