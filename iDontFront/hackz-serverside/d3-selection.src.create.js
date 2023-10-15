import creator from "./creator.js";
import select from "./select.js";
import { JSDOM } from "jsdom";
const dom = new JSDOM('<!DOCTYPE html><p>Hello</p>');

export default function(name) {
  let document = dom.window.document;
  return select(creator(name).call(document.documentElement));
}
