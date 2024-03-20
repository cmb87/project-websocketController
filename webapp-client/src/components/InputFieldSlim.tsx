import React from 'react'

interface IInputFieldSwitch {
  id: string
  label: string
  onChange: Function
  note?: string
}

interface IInputFieldSlim {
    id: string
    label: string
    type: string
    placeholder: string
    onChange: Function
    note?: string
}

interface IInputFieldSelectSlim {
  id: string
  label: string
  onChange: Function
  note?: string
  options: IOption[]
  disabled?:boolean
  value?: string
}

interface IOption {
  key: string | number
  value: string | number
}

const label_classes = 
 "block absolute text-gray-600 text-sm " +
 "md:text-left mb-1 md:mb-0 px-3 pt-1 "

 const input_classes = 
 "appearance-none text-l border border-blue-900 w-full pt-4 min-w-full" +
 "pb-1 px-3 text-blue-900 leading-tight focus:outline-none " +
 "focus:bg-white focus:border-blue-100 h-14 rounded"

export default function InputFieldSlim(props:IInputFieldSlim) {

  return (
    <div className="mb-4 px-2">
    <label className={label_classes} htmlFor={props.id}>
      {props.label}
    </label>
      <input
        className={input_classes}
        id={props.id}
        type={props.type}
        placeholder={props.placeholder}
        onChange={(e) => props.onChange(e.target.value)}
       />
      {props.note && <p className="text-blue-600  text-xs italic">{props.note}</p> }
    </div>
  )
}

export function InputFieldSelectSlim(props:IInputFieldSelectSlim) {

  return (
    <div className="mb-4 px-2">
    <label className={label_classes} htmlFor={props.id}>
      {props.label}
    </label>
      <select
        className={input_classes}
        id={props.id}
        disabled={props.disabled}
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
      >
        { props.options.map( ( o, index: number ) =>  <option key={index} value={o.value}>{o.key}</option>) }
      </select>

      {props.note && <p className="text-gray-600 text-xs italic">{props.note}</p> }
    </div>
  )
}

export function InputFieldSwitch(props:IInputFieldSwitch) {


  const label_classes = 
  "block absolute text-gray-100  text-l " +
  "md:text-left mb-0 md:mb-0 px-3 ml-3 pt-2"
 
  const input_classes = 
  "text-l w-full pt-2 " +
  "pb-1 px-3 text-blue-900 leading-tight focus:outline-none min-w-full" +
  "focus:bg-white focus:border-se-interaction-1 h-10 rounded w-full"

  return (
    <div className="mb-4 px-2">
    { props.label !== "" &&
      <label
        htmlFor={props.id}
        className={label_classes}
      >
        {props.label}
      </label>
    }
    <input
      id={props.id}
      className={input_classes}
      type="checkbox"
      onChange={() => props.onChange()}
    />

    {props.note && <p className="text-gray-600 text-xs italic">{props.note}</p> }
    </div>
  )
}


