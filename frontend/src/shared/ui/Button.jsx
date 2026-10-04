import "./Button.css";

export default function Button({
    children,
    variant="primary",
    onClick,
    type="button",
    disabled=false,
    style={}
}){

return (

<button
type={type}
onClick={onClick}
disabled={disabled}
style={style}
className={`ui-button ${variant}`}
>

{children}

</button>

)

}
