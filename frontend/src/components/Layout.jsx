import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";


export default function Layout(){

return (

<div style={{
    display:"flex",
    minHeight:"100vh"
}}>


<div style={{
    width:"220px",
    padding:"20px",
    borderRight:"1px solid #333"
}}>

<Sidebar />

</div>


<div style={{
    flex:1,
    padding:"30px",
    width:"calc(100% - 220px)",
    boxSizing:"border-box"
}}>

<Outlet />

</div>


</div>

)

}
