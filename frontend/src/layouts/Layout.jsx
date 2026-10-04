import { Outlet } from "react-router-dom";
import { useState } from "react";
import Sidebar from "./Sidebar";
import AppTopBar from "./AppTopBar";
import "./Layout.css";


export default function Layout(){

const [search, setSearch] = useState("");

return (

<div className="app-layout">


<Sidebar />

<AppTopBar search={search} setSearch={setSearch} />


<main className="page-content">

<Outlet context={{ search, setSearch }} />

</main>


</div>

)

}
