import "./Button.css";

export default function Button({
    children,
    variant="primary",
    onClick,
    type="button"
}){

return (

<button
type={type}
onClick={onClick}
className={`ui-button ${variant}`}
>

{children}

</button>

)

}
