import { Link } from "react-router-dom";

export default function Sidebar(){

return (

<div>

<h2>
AI Mail
</h2>

<nav>

<p>
<Link to="/dashboard">
Dashboard
</Link>
</p>

<p>
<Link to="/campaigns">
Campaigns
</Link>
</p>

</nav>

</div>

)

}
