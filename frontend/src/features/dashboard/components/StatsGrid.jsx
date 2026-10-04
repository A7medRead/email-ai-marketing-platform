import {
    Mail,
    MousePointerClick,
    ShieldCheck,
    AlertTriangle,
    UserMinus,
    Send
} from "lucide-react";

import StatsCard from "./StatsCard";

export default function StatsGrid({stats,marketing}){

    const openRate = stats.total_sent
        ? ((marketing.opened / stats.total_sent) * 100).toFixed(1)
        : 0;

    const clickRate = stats.total_sent
        ? ((marketing.clicked / stats.total_sent) * 100).toFixed(1)
        : 0;

    const attempted = Number(stats.total_sent || 0) + Number(stats.total_failed || 0);
    const deliveryRate = attempted
        ? (
            (Number(stats.total_sent || 0) /
            attempted) * 100
        ).toFixed(1)
        : 0;

    const bounceRate = attempted
        ? (
            (Number(stats.total_failed || 0) /
            attempted) * 100
        ).toFixed(1)
        : 0;


    const cards=[

        {
            title:"Emails Sent",
            value:stats.total_sent,
            icon:Send,
            color:"#427a77",
        },

        {
            title:"Open Rate",
            value:`${openRate}%`,
            icon:Mail,
            color:"#10b981",
        },

        {
            title:"Click Rate",
            value:`${clickRate}%`,
            icon:MousePointerClick,
            color:"#2563eb",
        },

        {
            title:"Delivery Rate",
            value:`${deliveryRate}%`,
            icon:ShieldCheck,
            color:"#f97316",
        },

        {
            title:"Bounce Rate",
            value:`${bounceRate}%`,
            icon:AlertTriangle,
            color:"#ef4444",
        },

        {
            title:"Unsubscribe Rate",
            value:"—",
            icon:UserMinus,
            color:"#5b8d89",
            subtitle:"Not tracked"
        }

    ];

    return(

        <div className="stats-grid">

            {

                cards.map(card=>(

                    <StatsCard
                        key={card.title}
                        {...card}
                    />

                ))

            }

        </div>

    )

}
