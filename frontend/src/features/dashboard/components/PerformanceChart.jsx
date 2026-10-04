import {
    ResponsiveContainer,
    LineChart,
    Line,
    CartesianGrid,
    Tooltip,
    XAxis,
    YAxis,
    Legend
} from "recharts";

export default function PerformanceChart({stats,marketing}){

    const data=[
        {
            day:"Mon",
            sent:Math.round(stats.total_sent*0.25),
            opened:Math.round(marketing.opened*0.22),
            clicked:Math.round(marketing.clicked*0.18)
        },
        {
            day:"Tue",
            sent:Math.round(stats.total_sent*0.45),
            opened:Math.round(marketing.opened*0.40),
            clicked:Math.round(marketing.clicked*0.35)
        },
        {
            day:"Wed",
            sent:Math.round(stats.total_sent*0.55),
            opened:Math.round(marketing.opened*0.50),
            clicked:Math.round(marketing.clicked*0.46)
        },
        {
            day:"Thu",
            sent:Math.round(stats.total_sent*0.82),
            opened:Math.round(marketing.opened*0.78),
            clicked:Math.round(marketing.clicked*0.70)
        },
        {
            day:"Fri",
            sent:Math.round(stats.total_sent*0.80),
            opened:Math.round(marketing.opened*0.75),
            clicked:Math.round(marketing.clicked*0.68)
        },
        {
            day:"Sat",
            sent:Math.round(stats.total_sent*0.72),
            opened:Math.round(marketing.opened*0.66),
            clicked:Math.round(marketing.clicked*0.55)
        },
        {
            day:"Sun",
            sent:stats.total_sent,
            opened:marketing.opened,
            clicked:marketing.clicked
        }
    ];

    return(

        <div className="dashboard-panel chart-panel">

            <div className="panel-header">

                <h3>Performance Overview</h3>

                <button className="chart-filter">
                    Last 7 days ▾
                </button>

            </div>

            <ResponsiveContainer width="100%" height={330}>

                <LineChart
                    data={data}
                    margin={{
                        top:10,
                        right:20,
                        left:0,
                        bottom:45
                    }}>

                    <CartesianGrid
                        stroke="#243043"
                        strokeDasharray="4 4"
                    />

                    <XAxis
                        dataKey="day"
                        stroke="#94a3b8"
                        fontSize={12}
                        tickMargin={8}
                    />

                    <YAxis
                        stroke="#94a3b8"
                        fontSize={12}
                        width={28}
                    />

                    <Tooltip
                        contentStyle={{
                            background:"#111827",
                            border:"1px solid #334155",
                            borderRadius:"12px",
                            color:"#fff"
                        }}
                    />

                    <Legend
                        verticalAlign="top"
                        align="left"
                        iconType="circle"
                        wrapperStyle={{paddingBottom:"8px",fontSize:"12px"}} iconSize={10}
                    />

                    <Line
                        type="monotone"
                        dataKey="sent"
                        stroke="#8b5cf6"
                        strokeWidth={2.5}
                        dot={{r:3}}
                        activeDot={{r:5}}
                    />

                    <Line
                        type="monotone"
                        dataKey="opened"
                        stroke="#22c55e"
                        strokeWidth={2.5}
                        dot={{r:3}}
                        activeDot={{r:5}}
                    />

                    <Line
                        type="monotone"
                        dataKey="clicked"
                        stroke="#3b82f6"
                        strokeWidth={2.5}
                        dot={{r:3}}
                        activeDot={{r:5}}
                    />

                </LineChart>

            </ResponsiveContainer>

        </div>

    );

}
