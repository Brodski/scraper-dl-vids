// idontfront-app\node_modules\@observablehq\plot\src
import {creator, select} from "d3";
import {maybeClip} from "./style.js";
// const { JSDOM } = require('jsdom');
import { JSDOM } from "jsdom";
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');

export function createContext(options = {}) {
  let {document = typeof window !== "undefined" ? window.document : undefined, clip} = options;
  console.log("FROM PLOT.JS FILE - Hello sucker")
  document = dom.window.document;
  return {document, clip: maybeClip(clip)};
}

export function create(name, {document}) {
  return select(creator(name).call(document.documentElement));
}
