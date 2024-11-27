
from datetime import datetime
from enum import Enum
from itertools import groupby
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field, computed_field
from app.new_models.Discount import CustomerDiscountType, TransactionDiscount
from app.new_models.Labtest import Labtest
from app.new_models.Package import Package, PackageType
from app.utils.utils import getLocalDateStr, getLocalTimeStr


class TransactionPackage(Package):
    discount: Optional[TransactionDiscount] = None

class TenderType(str, Enum):
    CASH = "cash"
    CHEQUE = "cheque"

class TransactionItem(Labtest):
    package: Optional[TransactionPackage] = None

    # @computed_field
    # @property
    # def packageId(self) -> str:
    #     return self.package.id


    
class CreateTransaction(BaseModel):
    branchId: str
    customerId: str
    cashierId: str
    referredById: Optional[str] = None
    requestedById: Optional[str] = None
    date: str = Field(default_factory=getLocalDateStr)
    transactionDate: str = Field(default_factory=getLocalTimeStr)
    transactionNo: str = Field(default_factory=lambda: str(uuid.uuid4()))
    transactionItems: List[TransactionItem] = Field(min_length=1)
    discounts: List[TransactionDiscount] = None
    tenderType: TenderType
    tenderAmount: float
    invoiceNumber: int = None

class Transaction(BaseModel):
    branch: Optional[object]
    customer: Optional[object]
    cashier: Optional[object]
    referredBy: Optional[object]
    requestedBy: Optional[object]
    date: str
    transactionDate: str
    transactionNo: str
    transactionItems: List[TransactionItem]
    discounts: List[TransactionDiscount] = None
    tenderType: TenderType
    tenderAmount: float
    invoiceNumber: int
    # branchId: str
    # customerId: str
    # referredById: str = None
    # requestedById: str = None
    # date: str = Field(default_factory=getLocalDateStr)
    # transactionDate: str = Field(default_factory=getLocalTimeStr)
    # transactionNo: str = Field(default_factory=lambda: str(uuid.uuid4()))
    # transactionItems: List[TransactionItem] = Field(min_length=1)
    # discounts: List[TransactionDiscount] = None
    # tenderType: TenderType
    # tenderAmount: float

    @computed_field
    @property
    def totalGrossSales(self) -> float:
        return self._sum(self._getItemPrices(self.transactionItems))

    @computed_field
    @property
    def totalNetSales(self) -> float:
        totalSales = self._computeTotalSales()
        totalDiscount = self._computeTotalMemberDiscount(totalSales)
        totalNetSales = totalSales - totalDiscount
        return totalNetSales    

    @computed_field
    @property
    def totalDiscount(self) -> float:
        return self.totalGrossSales - self.totalNetSales

    @computed_field
    @property
    def totalMemberDiscount(self) -> float:
        totalSales = self._computeTotalSales()
        totalDiscount = self._computeTotalMemberDiscount(totalSales)
        return totalDiscount

    @computed_field
    @property
    def change(self) -> float:
        return self.tenderAmount - self.totalNetSales
    
    @property
    def transactionDateObject(self) -> datetime:
        return datetime.fromisoformat(self.transactionDate)
    
    def _computeTotalMemberDiscount(self, totalSales) -> float:
        discounts = self._filterDiscounts(lambda i: i.customerDiscountType == CustomerDiscountType.GOVERNMENT_BENEFICIARY)
        totalDiscount = self._sumTotalDiscount(discounts, totalSales)
        return totalDiscount

    def _computeTotalSales(self) -> float:
        packageSales = self._computeTotalPackageSales()
        promoSales = self._computeTotalPromoSales()
        totalSales = packageSales + promoSales
        return totalSales

    def _computeTotalPackageSales(self) -> float:
        items = self._filterItemsByNotType(PackageType.PROMO)
        totalPrice =  self._sum(self._getItemPrices(items))

        discounts = self._filterDiscounts(lambda i: i.packageType != PackageType.PROMO and i.customerDiscountType != CustomerDiscountType.GOVERNMENT_BENEFICIARY)
        totalDiscount = self._sumTotalDiscount(discounts, totalPrice)
        return totalPrice - totalDiscount
    
    def _computeTotalPromoSales(self) -> float:
        totalPromoPrice: float = 0.0

        items = self._filterItems(lambda i: i.package is not None and i.package.type == PackageType.PROMO)
        items = groupby(items, lambda i: i.package.id)

        for _, groupItems in items:
            groupItems = list(groupItems)
            discount = groupItems[0].package.discount

            prices = self._getItemPrices(groupItems)
            totalPrice = self._sum(prices)
            totalPrice -= discount.calculateTotalDiscount(totalPrice)

            totalPromoPrice += totalPrice
            
        return totalPromoPrice
   
    def _filterItems(self, func) -> List[TransactionItem]:
        return list(filter(func, self.transactionItems))

    def _filterItemsByNotType(self, type: PackageType) -> List[TransactionItem]:
        #Filter all items that exactly unmatch with type even if item package is none
        return self._filterItems(lambda i: i.package.type != type)
    
    def _filterItemsByPackage(self, packageId: str, type: PackageType) -> List[TransactionItem]:
        #Short circuit - filter all items that package is not none and match with id and type
        return self._filterItems(lambda i: i.package != None and (i.package.id == packageId and i.package.type == type))

    def _filterDiscounts(self, func) -> List[TransactionDiscount]:
        if(self.discounts == None):
            return []
        return list(filter(func, self.discounts))
    
    def _getItemPrices(self, items: List[TransactionItem]):
        return list(map(lambda i: i.price, items))
    
    def _getDiscountValues(self, discounts: List[TransactionDiscount], sales: float):
        values: List[float] = []
        for discount in discounts:
            values.append(discount.calculateTotalDiscount(sales))
        return values
    
    def _sumTotalDiscount(self, discounts: List[TransactionDiscount], sales: float):
        discounts = self._getDiscountValues(discounts, sales)
        return self._sum(discounts)
    
    def _sum(self, items):
        sum: float = 0
        for item in items:
            sum += item
        return sum
    