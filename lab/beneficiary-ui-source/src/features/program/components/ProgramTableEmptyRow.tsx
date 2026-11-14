export default function ProgramTableEmptyRow({ index }: { index: number }) {
    return (
        <tr
            className={`${index % 2 === 0 ? "bg-white" : "bg-[#F5F5F5]"} lg:h-[53px] xl:h-[53px] 2xl:h-[56px]`}
        >
            <td className="px-[30px]">
                <div className="lg:h-5 xl:h-5 2xl:h-6 w-3/4 bg-none"></div>
            </td>
            <td className="px-[30px]">
                <div className="lg:h-5 xl:h-5 2xl:h-6 w-1/2 bg-none"></div>
            </td>
            <td className="lg:py-[14px] xl:py-[14px] 2xl:py-[16px] flex">
                <div className="lg:h-5 xl:h-5 2xl:h-6 w-[60px] bg-none"></div>
            </td>
        </tr>
    );
}
