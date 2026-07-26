import "./EmptyState.css";

export default function EmptyState({title="No data found",message=""}){

return (

<div className="empty-state">

<h3>
{title}
</h3>

{
message &&
<p>
{message}
</p>
}

</div>

);

}
